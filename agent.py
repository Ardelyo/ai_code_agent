# agent.py
import argparse
import json
import os
import re
import sys
from pathlib import Path
import yaml # pip install PyYAML
import tempfile # For temporary markdown file

# --- Import your tools and connectors ---
import replacer_core 
from tools import FileSystemTool, LLMTool, CodeAnalysisTool

# --- Helper Classes and Functions (Config, get_yes_no_input - same as before) ---
class Config:
    def __init__(self, config_path_str="config_agent.yaml"):
        self.data = {}
        config_path = Path(config_path_str)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_yaml = yaml.safe_load(f)
                    if loaded_yaml: 
                        self.data = loaded_yaml
                print(f"INFO: Loaded configuration from {config_path}")
            except yaml.YAMLError as e:
                print(f"WARNING: Error parsing {config_path}: {e}. Using defaults/CLI args.")
        else:
            print(f"INFO: Config file {config_path} not found. Using defaults/CLI args.")

    def get(self, key, default=None, cli_override=None):
        if cli_override is not None:
            return cli_override
        env_val = os.getenv(key.upper().replace("-", "_"))
        if env_val is not None:
            return env_val
        yaml_val = self.data.get(key) 
        if yaml_val is not None:
            return yaml_val
        return default

def get_yes_no_input(prompt_message: str, default_yes: bool = True) -> bool:
    suffix = " (Y/n)" if default_yes else " (y/N)"
    while True:
        try:
            answer = input(f"{prompt_message}{suffix}: ").strip().lower()
            if not answer: return default_yes
            if answer in ['y', 'yes']: return True
            if answer in ['n', 'no']: return False
            print("Invalid input. Please enter 'y', 'yes', 'n', or 'no'.")
        except EOFError: return default_yes
        except KeyboardInterrupt: print("\nInput cancelled."); return False

def simple_ai_planner_and_executor(
    user_prompt: str, 
    llm_tool: LLMTool, 
    fs_tool: FileSystemTool,
    code_tool: CodeAnalysisTool,
    default_model_choice: str,
    dry_run: bool,
    no_backup: bool
    ):
    print(f"\n🤖 AI Agent received prompt: \"{user_prompt}\"")

    # --- Stage 1: Identify Target File ---
    target_file_path_str = ""
    file_match = re.search(r"(?:in|modify|update|refactor|edit|change|process)\s+(?:file\s+)?['\"]?([\w\/\.\-\_]+\.\w+)['\"]?", user_prompt, re.IGNORECASE)
    if file_match:
        target_file_path_str = file_match.group(1)
        print(f"INFO: Tentatively identified target file from prompt: '{target_file_path_str}'")
    else:
        target_file_path_str = input("AI> Could not determine target file from prompt. Please enter file path: ").strip()
        if not target_file_path_str:
            print("ERROR: Target file path is required. Exiting.")
            return

    target_file_path = Path(target_file_path_str)
    original_file_content = "" # Initialize to empty string
    original_file_lines = []

    if target_file_path.exists():
        original_file_content = fs_tool.read_file(str(target_file_path))
        if original_file_content is None: # fs_tool.read_file now returns None on error
            print(f"ERROR: Failed to read existing target file '{target_file_path}'. Exiting.")
            return
        original_file_lines = original_file_content.splitlines()
        print(f"INFO: Target file '{target_file_path}' exists and was read.")
    else:
        if not get_yes_no_input(f"AI> Target file '{target_file_path}' does not exist. Create it?", default_yes=False):
            print("INFO: Operation cancelled by user.")
            return
        print(f"INFO: Will create new file: '{target_file_path}'")
        # original_file_content remains "" for new files

    # --- Stage 2: Use LLM to generate block_identifier ---
    print(f"\nAI> Attempting to identify the code block to modify in '{target_file_path_str}'...")
    file_context_snippet = code_tool.get_file_context_snippet(original_file_content, max_lines=100, max_chars=4000)
    
    block_identifier_json = llm_tool.generate_json_block_identifier(
        user_prompt, 
        file_context_snippet,
        default_model_choice 
    )

    if not block_identifier_json:
        print("ERROR: AI failed to generate a valid block identifier. Cannot proceed.")
        # Potential future enhancement: call gather_instructions_interactively for block_identifier
        return
    
    print(f"AI> Identified block with: {json.dumps(block_identifier_json, indent=2)}")

    # --- Stage 3: Use LLM to generate replacement code ---
    original_block_snippet_for_llm = None
    if original_file_lines and block_identifier_json:
        temp_find_result = replacer_core.find_target_block(original_file_lines, block_identifier_json, str(target_file_path))
        if temp_find_result:
            s_idx, e_idx, _ = temp_find_result
            if 0 <= s_idx <= e_idx < len(original_file_lines):
                 original_block_snippet_for_llm = "\n".join(original_file_lines[s_idx : e_idx+1])
                 print(f"INFO: Extracted original block snippet for LLM context (length {len(original_block_snippet_for_llm)} chars).")
            else: 
                if s_idx == e_idx + 1: 
                    print("INFO: Identified an insertion point, no original block content to replace.")
                else:
                    print(f"WARNING: find_target_block returned invalid range [{s_idx}-{e_idx}] for existing file. Proceeding without original block snippet.")
        else:
            print("WARNING: Could not find the specified block in the existing file to provide as context for replacement code generation.")

    print(f"\nAI> Generating replacement code based on your prompt...")
    # This is the full list of lines for the replacement code
    full_replacement_code_lines = llm_tool.generate_code_snippet(
        user_request=user_prompt, 
        original_code_snippet=original_block_snippet_for_llm,
        surrounding_context=file_context_snippet if not original_block_snippet_for_llm else None, 
        model_choice=default_model_choice 
    )

    if not full_replacement_code_lines or \
       (len(full_replacement_code_lines) == 1 and full_replacement_code_lines[0].startswith("Error:")) or \
       (len(full_replacement_code_lines) == 0 and not (original_block_snippet_for_llm and "delete" in user_prompt.lower())): # Allow empty if it's a deletion
        print("ERROR: AI failed to generate replacement code or generated empty code unexpectedly. Cannot proceed.")
        return

    # --- Stage 3.5: Save full generated code to a temporary markdown file for review ---
    preview_file_path = None
    if full_replacement_code_lines: # Only save if there's something to show
        try:
            # Determine language for markdown code block (simple heuristic)
            target_ext = target_file_path.suffix.lower().lstrip('.')
            lang_hint = target_ext if target_ext in ["py", "js", "html", "css", "java", "cpp", "csharp", "xml", "json", "yaml", "md"] else ""

            # Create a temporary file that will be automatically deleted
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(f"``` {lang_hint}\n")
                tmp_file.write("\n".join(full_replacement_code_lines))
                tmp_file.write("\n```")
                preview_file_path = tmp_file.name
            print(f"\n✨ AI> Full generated replacement code has been saved for your review to:\n      {preview_file_path}")
            print("      (This file will be deleted after the script finishes or on error).")
        except Exception as e:
            print(f"WARNING: Could not save generated code to a temporary file for review: {e}")

    print("\nAI> Preview of generated replacement code (first 5 lines):")
    for line in full_replacement_code_lines[:5]:
        print(f"  {line}")
    if len(full_replacement_code_lines) > 5: print("  ...")


    # --- Stage 4: Construct and Confirm Full Instruction ---
    instruction = {
        "target_file": str(target_file_path),
        "block_identifier": block_identifier_json, # Use the LLM generated one
        "replacement_code": full_replacement_code_lines, # Use the FULL code here
        "indentation_handling": "match_original_block_start", 
        "backup_original_file": not no_backup, 
        "create_if_not_exists": not target_file_path.exists() 
    }

    print("\n--- AI Proposed Action ---")
    print(f"Target File: {instruction['target_file']}")
    print(f"Block Identifier Type: {instruction['block_identifier'].get('type')}")
    # ... (rest of the print summary for block_identifier details) ...
    if 'name' in instruction['block_identifier']: print(f"Name/Function/Class: {instruction['block_identifier']['name']}")
    if 'start_marker_regex' in instruction['block_identifier']:
        print(f"Start Marker Regex: {instruction['block_identifier']['start_marker_regex']}")
        print(f"End Marker Regex: {instruction['block_identifier']['end_marker_regex']}")
        print(f"Inclusive Markers: {instruction['block_identifier'].get('inclusive_markers', False)}")

    # Preview for instruction also shows first 5 lines
    print(f"Replacement Code (first 5 lines - see temp file for full code):")
    for line in instruction['replacement_code'][:5]: print(f"  {line}")
    if len(instruction['replacement_code']) > 5: print("  ...")
    
    proceed = get_yes_no_input("\nAI> Proceed with this action?", default_yes=not dry_run)
    
    if not proceed:
        print("INFO: Operation cancelled by user.")
        if preview_file_path and os.path.exists(preview_file_path): # Clean up temp file if user cancels
            try:
                os.remove(preview_file_path)
                print(f"INFO: Temporary preview file {preview_file_path} deleted.")
            except OSError as e:
                print(f"WARNING: Could not delete temporary preview file {preview_file_path}: {e}")
        return

    # --- Stage 5: Execute ---
    try:
        if not no_backup and instruction.get('backup_original_file') and target_file_path.exists() and not dry_run:
            replacer_core.backup_file(target_file_path)

        if not original_file_lines and not target_file_path.exists() and instruction.get('create_if_not_exists'):
            final_content_lines = replacer_core.apply_indentation(
                instruction['replacement_code'], 
                "", 
                instruction['indentation_handling']
            )
            print(f"INFO: Preparing to create new file '{target_file_path}' with generated content.")
        else:
            final_content_lines = replacer_core.perform_replacement_on_content(
                original_lines=original_file_lines,
                block_identifier=instruction['block_identifier'],
                replacement_code=instruction['replacement_code'], # Pass FULL code
                indentation_handling=instruction['indentation_handling'],
                target_file_path_str=str(target_file_path)
            )

        if final_content_lines is None:
            print(f"ERROR: Failed to determine final content for '{target_file_path}'. Block might not have been found.")
            return

        modified_file_content = "\n".join(final_content_lines) + "\n"

        if dry_run:
            print(f"\n--- Dry Run: Proposed changes for {target_file_path.name} ---")
            replacer_core.show_diff(original_file_content, modified_file_content, target_file_path.name)
            print("--- End Dry Run ---")
        else:
            success = fs_tool.write_to_file(str(target_file_path), final_content_lines, create_dirs=True)
            if success:
                print(f"✅ AI Agent successfully modified '{target_file_path}'.")
            else:
                print(f"❌ AI Agent failed to write modifications to '{target_file_path}'.")
    finally: # Ensure temp file is deleted whether successful or not (if user proceeded)
        if preview_file_path and os.path.exists(preview_file_path):
            try:
                os.remove(preview_file_path)
                print(f"INFO: Temporary preview file {preview_file_path} deleted.")
            except OSError as e:
                print(f"WARNING: Could not delete temporary preview file {preview_file_path}: {e}")


# --- Main Function (defined after helpers) ---
def main():
    parser = argparse.ArgumentParser(description="AI-Powered Code Agent to modify files based on natural language.")
    # ... (argparse setup remains the same as before) ...
    parser.add_argument("user_prompt", help="Natural language instruction for the code modification.")
    parser.add_argument("--model", help="LLM model choice (e.g., 'openrouter/model-id', 'ollama/model-name'). Overrides config.", default=None)
    parser.add_argument("--config", help="Path to YAML configuration file.", default="config_agent.yaml")
    
    parser.add_argument("--openrouter-api-key", help="OpenRouter API Key. Overrides config/env.", default=None)
    parser.add_argument("--openrouter-site-url", help="OpenRouter Site URL for referrer. Overrides config/env.", default=None)
    parser.add_argument("--openrouter-app-name", help="OpenRouter App Name for referrer. Overrides config/env.", default=None)
    parser.add_argument("--ollama-base-url", help="Ollama base URL (e.g., http://localhost:11434). Overrides config/env.", default=None)
    parser.add_argument("--ollama-default-model", help="Default Ollama model if 'ollama/' is used without specific model. Overrides config/env.", default=None)

    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing to file.")
    parser.add_argument("--no-backup", action="store_true", help="Do not create backup of the target file.")
    
    args = parser.parse_args()
    config_loader = Config(args.config) 

    cfg_data_for_tools = {
        "OPENROUTER_API_KEY": config_loader.get("OPENROUTER_API_KEY", cli_override=args.openrouter_api_key),
        "OPENROUTER_SITE_URL": config_loader.get("OPENROUTER_SITE_URL", cli_override=args.openrouter_site_url),
        "OPENROUTER_REFERRER": config_loader.get("OPENROUTER_REFERRER", cli_override=args.openrouter_app_name),
        "OLLAMA_BASE_URL": config_loader.get("OLLAMA_BASE_URL", default="http://localhost:11434", cli_override=args.ollama_base_url),
        "OLLAMA_DEFAULT_MODEL": config_loader.get("OLLAMA_DEFAULT_MODEL", cli_override=args.ollama_default_model),
        "DEFAULT_MODEL_CHOICE": config_loader.get("DEFAULT_MODEL_CHOICE", cli_override=args.model)
    }
    
    # ... (rest of main function, LLM config checks, tool initializations - remains the same) ...
    if not cfg_data_for_tools.get("DEFAULT_MODEL_CHOICE"):
        print("ERROR: No default model specified. Use --model or set DEFAULT_MODEL_CHOICE in config/env.")
        sys.exit(1)
    if cfg_data_for_tools["DEFAULT_MODEL_CHOICE"].startswith("openrouter/") and not cfg_data_for_tools.get("OPENROUTER_API_KEY"):
        print("ERROR: OpenRouter model selected, but OPENROUTER_API_KEY is not set in config, CLI, or environment.")
        sys.exit(1)

    llm_tool = LLMTool(cfg_data_for_tools)
    fs_tool = FileSystemTool()
    code_tool = CodeAnalysisTool()

    try:
        simple_ai_planner_and_executor(
            args.user_prompt,
            llm_tool,
            fs_tool,
            code_tool,
            cfg_data_for_tools["DEFAULT_MODEL_CHOICE"],
            args.dry_run,
            args.no_backup
        )
    except KeyboardInterrupt:
        print("\n🤖 Agent operation cancelled by user (Ctrl+C).")
        # Attempt to clean up temp file if one was created and path is known
        # This is tricky because preview_file_path is local to simple_ai_planner_and_executor
        # A more robust solution would involve passing its state or using a context manager.
        # For now, we'll rely on the finally block within simple_ai_planner_and_executor.
        sys.exit(130)
    except Exception as e:
        print(f"FATAL ERROR in agent execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# --- Entry Point ---
if __name__ == "__main__":
    main()