# agent.py
import argparse
import sys
import yaml # pip install PyYAML
from pathlib import Path
import os
import json # For LLM action parsing

# --- Project Imports ---
import replacer_core
from tools import FileSystemTool, LLMTool, CodeAnalysisTool, ChangeOrchestratorTool
from connectors import OpenRouterConnector, OllamaConnector # Assuming these are stable
from advanced_planner_tools import StateManager, TaskDecomposer, ReActPlannerExecutor, ClarificationModule

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
            print(f"INFO: Config file '{config_path}' not found. Using defaults/CLI args.")

    def get(self, key, default=None, cli_override=None):
        if cli_override is not None:
            return cli_override

        keys = key.split('.')
        value_from_yaml = self.data
        try:
            for k_part in keys:
                if isinstance(value_from_yaml, dict):
                    value_from_yaml = value_from_yaml[k_part]
                else:
                    value_from_yaml = None
                    break
            if value_from_yaml is not None:
                if isinstance(default, bool) and isinstance(value_from_yaml, str):
                    return value_from_yaml.lower() in ['true', '1', 't', 'y', 'yes']
                if isinstance(default, int) and isinstance(value_from_yaml, (str,float)): # Allow string/float from YAML for int
                    try: return int(value_from_yaml)
                    except ValueError: pass # Fall through if not convertible
                if isinstance(default, float) and isinstance(value_from_yaml, (str,int)): # Allow string/int from YAML for float
                    try: return float(value_from_yaml)
                    except ValueError: pass # Fall through
                return value_from_yaml
        except (KeyError, TypeError):
            value_from_yaml = None

        env_key = key.upper().replace(".", "_").replace("-", "_")
        env_val = os.getenv(env_key)
        if env_val is not None:
            if isinstance(default, bool): return env_val.lower() in ['true', '1', 't', 'y', 'yes']
            if isinstance(default, int): return int(env_val)
            if isinstance(default, float): return float(env_val)
            return env_val
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

def run_advanced_agent(user_prompt: str, config_loader: Config, op_mode_name: str,
                       project_base_path: Path,
                       dry_run: bool, no_backup: bool, skip_confirmation: bool):
    print(f"🤖 AI Agent activated. Operational Mode: {op_mode_name.upper()}")
    print(f"User Prompt: \"{user_prompt}\"")
    print(f"Project Base Path: {project_base_path.resolve()}")

    mode_conf_prefix = f"operational_modes.{op_mode_name}"

    def get_mode_config(specific_key_suffix, general_config_key=None, ultimate_fallback_value=None):
        mode_specific_value = config_loader.get(f"{mode_conf_prefix}.{specific_key_suffix}", default=ultimate_fallback_value) # Pass fallback to get
        if mode_specific_value is not None: # Check if get returned non-None
             # If mode_specific_value is identical to ultimate_fallback_value, it means it wasn't found in mode-specific.
             # So then try general_config_key.
            if mode_specific_value == ultimate_fallback_value and general_config_key : # Check if it was truly a fallback
                general_value = config_loader.get(general_config_key, default=ultimate_fallback_value)
                return general_value # This will be ultimate_fallback_value if general_config_key also not found
            return mode_specific_value # Found in mode-specific

        if general_config_key: # Mode specific was None, try general
            general_value = config_loader.get(general_config_key, default=ultimate_fallback_value)
            return general_value
        
        return ultimate_fallback_value # Ultimate fallback if all else fails

    planning_model = get_mode_config("default_planning_model", "DEFAULT_MODEL_CHOICE", "ollama/mistral:7b")
    generation_model = get_mode_config("default_generation_model", "DEFAULT_MODEL_CHOICE", "ollama/mistral:7b")
    allow_task_decomposition = get_mode_config("allow_task_decomposition", None, True) # No general key, direct fallback
    max_api_calls = get_mode_config("max_api_calls_openrouter", None, 10)
    max_ollama_iterations = get_mode_config("max_planning_iterations_ollama", None, 10)
    allow_clarification = get_mode_config("allow_clarification_loops", None, True)
    max_gen_tokens = get_mode_config("max_tokens_generation", None, 2048)

    print(f"INFO: Using Planning Model: {planning_model}")
    print(f"INFO: Using Generation Model: {generation_model}")
    print(f"INFO: Task Decomposition: {'Enabled' if allow_task_decomposition else 'Disabled'}")
    print(f"INFO: Clarification Loops: {'Enabled' if allow_clarification else 'Disabled'}")
    print(f"INFO: Max OpenRouter API Calls: {max_api_calls}")
    print(f"INFO: Max Ollama/Sub-task Iterations: {max_ollama_iterations}")
    print(f"INFO: Max Generation Tokens: {max_gen_tokens}")


    state_manager = StateManager(
        user_prompt=user_prompt,
        operational_mode=op_mode_name,
        mode_config={
            "planning_model": planning_model,
            "generation_model": generation_model,
            "max_api_calls_openrouter": int(max_api_calls), # Ensure int
            "max_planning_iterations_ollama": int(max_ollama_iterations), # Ensure int
            "allow_clarification_loops": bool(allow_clarification), # Ensure bool
            "max_tokens_generation": int(max_gen_tokens) # Ensure int
        },
        project_base_path=project_base_path,
        dry_run=dry_run
    )

    llm_tool_config_data = {
        "OPENROUTER_API_KEY": config_loader.get("openrouter.api_key"),
        "OPENROUTER_SITE_URL": config_loader.get("openrouter.site_url"),
        "OPENROUTER_REFERRER": config_loader.get("openrouter.app_name"),
        "OLLAMA_BASE_URL": config_loader.get("ollama.base_url", "http://localhost:11434"),
        "DEFAULT_MODEL_CHOICE": config_loader.get("DEFAULT_MODEL_CHOICE", "ollama/mistral:7b"),
        "MAX_TOKENS_GENERATION": int(max_gen_tokens)
    }
    llm_tool = LLMTool(llm_tool_config_data)
    fs_tool = FileSystemTool(project_base_path=project_base_path)
    code_analysis_tool = CodeAnalysisTool()
    change_orchestrator_tool = ChangeOrchestratorTool()

    task_decomposer = TaskDecomposer(llm_tool, state_manager)
    clarification_module = ClarificationModule(state_manager)
    
    available_tools = {
        "FileSystemTool": fs_tool,
        "LLMTool": llm_tool,
        "CodeAnalysisTool": code_analysis_tool,
        "ChangeOrchestratorTool": change_orchestrator_tool,
        "RequestClarificationTool": clarification_module
    }
    react_planner = ReActPlannerExecutor(llm_tool, state_manager, available_tools, clarification_module)

    if allow_task_decomposition:
        print("\n--- Stage 1: Task Decomposition ---")
        plan = task_decomposer.decompose()
        if not plan or not plan.get("sub_tasks"):
            print("INFO: Task decomposition did not yield sub-tasks or failed. Proceeding with original prompt as single task.")
            plan = {
                "overall_goal": user_prompt,
                "sub_tasks": [{"id": "main_task_0", "description": user_prompt, "complexity": "unknown", "status": "pending"}]
            }
        state_manager.set_plan(plan)
    else:
        print("\n--- Stage 1: Skipping Task Decomposition (as per mode config) ---")
        plan = {
            "overall_goal": user_prompt,
            "sub_tasks": [{"id": "main_task_0", "description": user_prompt, "complexity": "unknown", "status": "pending"}]
        }
        state_manager.set_plan(plan)

    print("\n--- Stage 2: Plan Execution ---")
    all_directive_groups = react_planner.execute_plan()

    if not all_directive_groups:
        print("INFO: Planner did not produce any change directives after all sub-tasks. Exiting.")
        return

    print("\n--- Stage 3: Consolidating All Proposed Changes ---")
    flat_directives = []
    if all_directive_groups and isinstance(all_directive_groups, list):
        for group in all_directive_groups:
            if group and isinstance(group, list):
                flat_directives.extend(d for d in group if isinstance(d, dict))
    
    if not flat_directives:
        print("INFO: No valid changes (directives) were proposed by the agent after plan execution.")
        return

    print("Summary of proposed changes:")
    for i, directive_group in enumerate(all_directive_groups):
        if directive_group and isinstance(directive_group, list):
            # Try to get sub-task description for better summary
            sub_task_desc = f"Step {i+1}"
            if state_manager.plan and state_manager.plan.get("sub_tasks") and i < len(state_manager.plan["sub_tasks"]):
                sub_task_id_ref = state_manager.plan["sub_tasks"][i].get("id")
                sub_task_desc = f"Sub-task '{state_manager.plan['sub_tasks'][i].get('id', i+1)}': {state_manager.plan['sub_tasks'][i].get('description', 'N/A')[:50]}..."

            print(f"  From {sub_task_desc}:")
            for directive in directive_group:
                if isinstance(directive, dict):
                     print(f"    - File: {directive.get('file_path', 'N/A')}, Type: {directive.get('change_type', 'N/A')}, Code lines: {len(directive.get('code_snippet', []))}")

    preview_content = ["# AI Code Agent Proposed Changes\n"]
    for i, directive_group in enumerate(all_directive_groups):
        if directive_group and isinstance(directive_group, list):
            sub_task_header = f"From Sub-task/Plan Step {i+1}"
            if state_manager.plan and state_manager.plan.get("sub_tasks") and i < len(state_manager.plan["sub_tasks"]):
                 sub_task_header = f"From Sub-task '{state_manager.plan['sub_tasks'][i].get('id', i+1)}': {state_manager.plan['sub_tasks'][i].get('description', '')}"

            preview_content.append(f"\n## {sub_task_header}\n")
            for directive in directive_group:
                if isinstance(directive, dict):
                    preview_content.append(f"### File: {directive.get('file_path')}\n")
                    preview_content.append(f"Change Type: {directive.get('change_type')}\n")
                    if directive.get('target_element_selector'):
                         preview_content.append(f"Target Selector: {directive.get('target_element_selector')}\n")
                    if directive.get('block_identifier'): # block_identifier could be None
                         preview_content.append(f"Target Block Identifier: {json.dumps(directive.get('block_identifier'))}\n")
                    
                    code_snippet_preview = directive.get('code_snippet', [])
                    # Ensure code_snippet_preview is a list of strings
                    if not isinstance(code_snippet_preview, list):
                        code_snippet_preview = str(code_snippet_preview).splitlines()
                    code_snippet_str = "\n".join(code_snippet_preview)

                    preview_content.append("```\n" + code_snippet_str + "\n```\n")
    
    preview_file_path = Path("ai_agent_preview.md")
    try:
        preview_file_path.write_text("\n".join(preview_content), encoding='utf-8')
        print(f"\n✨ Detailed preview of all changes saved to: {preview_file_path.resolve()}")
    except Exception as e:
        print(f"WARNING: Could not write preview file: {e}")

    if skip_confirmation or get_yes_no_input("\nAI> Proceed with applying these changes?", default_yes=not dry_run):
        if dry_run:
            print("\n--- Dry Run Mode: Simulating application of changes. ---")
            # In dry run, ChangeOrchestratorTool will show diffs but not write
            change_orchestrator_tool.apply_all_changes(
                all_directive_groups, fs_tool, replacer_core, state_manager, no_backup
            )
            print("--- Dry Run Complete. No files modified. ---")
        else:
            print("\n--- Stage 4: Applying Changes ---")
            final_success = change_orchestrator_tool.apply_all_changes(
                all_directive_groups, fs_tool, replacer_core, state_manager, no_backup
            )
            if final_success:
                print("✅ AI Agent successfully applied all changes.")
            else:
                print("❌ AI Agent encountered errors during change application. Some changes might be partial. Please review.")
    else:
        print("INFO: Operation cancelled by user. No changes applied.")
    print("\n🤖 AI Agent run complete.")

def main():
    parser = argparse.ArgumentParser(description="Advanced AI-Powered Code Agent.")
    parser.add_argument("user_prompt", help="Natural language instruction for the code modification.")
    parser.add_argument("--project-path", "-p", help="Absolute or relative path to the project's root directory.", default=None)
    parser.add_argument("--config", help="Path to YAML configuration file.", default="config_agent.yaml")
    parser.add_argument("--mode", help="Operational mode (efficient, normal, max_energy). Overrides config default.", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing to file.")
    parser.add_argument("--no-backup", action="store_true", help="Do not create backups of target files.")
    parser.add_argument("--yes", action="store_true", help="Auto-confirm prompts (use with caution!).")
    parser.add_argument("--planning-model", help="Override planning model for current run.", default=None)
    parser.add_argument("--generation-model", help="Override generation model for current run.", default=None)

    args = parser.parse_args()
    config_loader = Config(args.config)

    project_path_str = args.project_path
    if not project_path_str:
        print("INFO: Project path not specified via --project-path argument.")
        while True:
            try:
                raw_path_input = input("Please enter the path to your project's root directory (or leave blank for current dir): ")
                raw_path = raw_path_input.strip().strip('"').strip("'")
                if not raw_path:
                    project_path_str = "."
                    print(f"INFO: Using current directory as project root: {Path('.').resolve()}")
                    break
                potential_path = Path(raw_path)
                if potential_path.exists() and potential_path.is_dir():
                    project_path_str = raw_path
                    print(f"INFO: Using project root: {potential_path.resolve()}")
                    break
                else:
                    print(f"ERROR: Path '{raw_path_input}' (processed as '{raw_path}') does not exist or is not a directory. Please try again.")
            except KeyboardInterrupt: print("\nOperation cancelled by user."); sys.exit(130)
            except Exception as e: print(f"An error occurred: {e}")
    
    project_base_path = Path(project_path_str).resolve()
    if not project_base_path.is_dir():
        print(f"FATAL ERROR: Resolved project path '{project_base_path}' is not a valid directory. Exiting.")
        sys.exit(1)

    op_mode_name = args.mode if args.mode else config_loader.get("DEFAULT_OPERATIONAL_MODE", "normal")
    
    # Apply CLI model overrides to the config_loader.data before passing to run_advanced_agent
    if args.planning_model:
        modes_data = config_loader.data.setdefault('operational_modes', {})
        mode_settings = modes_data.setdefault(op_mode_name, {})
        mode_settings['default_planning_model'] = args.planning_model
        print(f"INFO: Overriding planning model for '{op_mode_name}' mode with: {args.planning_model}")
    if args.generation_model:
        modes_data = config_loader.data.setdefault('operational_modes', {})
        mode_settings = modes_data.setdefault(op_mode_name, {})
        mode_settings['default_generation_model'] = args.generation_model
        print(f"INFO: Overriding generation model for '{op_mode_name}' mode with: {args.generation_model}")


    try:
        run_advanced_agent(
            args.user_prompt, config_loader, op_mode_name, project_base_path,
            args.dry_run, args.no_backup, args.yes
        )
    except KeyboardInterrupt: print("\n🤖 Agent operation cancelled by user (Ctrl+C)."); sys.exit(130)
    except Exception as e:
        print(f"FATAL ERROR in agent execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()