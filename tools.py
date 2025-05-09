# tools.py
import json
import re
from pathlib import Path
from connectors import OpenRouterConnector, OllamaConnector # Assuming these are stable

class FileSystemTool:
    def __init__(self, project_base_path: Path | None = None): # Allow None for testing or if not set
        self.project_base_path = project_base_path if project_base_path else Path(".") # Default to CWD

    def _resolve_path(self, file_path_str: str) -> Path:
        path_obj = Path(file_path_str)
        if path_obj.is_absolute():
            return path_obj.resolve()
        return (self.project_base_path / path_obj).resolve()

    def read_file(self, file_path_str: str) -> str | None:
        if not file_path_str or not isinstance(file_path_str, str):
            print(f"ERROR: FileSystemTool.read_file received invalid file_path_str: {file_path_str}")
            return None
        resolved_path = self._resolve_path(file_path_str)
        try:
            if resolved_path.exists() and resolved_path.is_file():
                content = resolved_path.read_text(encoding='utf-8')
                print(f"INFO: FileSystemTool: Read file '{resolved_path}' ({len(content)} chars).")
                return content
            else:
                print(f"ERROR: FileSystemTool: File not found or is not a file: {resolved_path}")
                return None # Explicitly return None
        except Exception as e:
            print(f"ERROR: FileSystemTool: Could not read file {resolved_path}: {e}")
            return None

    def write_to_file(self, file_path_str: str, content_lines: list[str], create_dirs: bool = True) -> bool:
        if not file_path_str or not isinstance(file_path_str, str):
            print(f"ERROR: FileSystemTool.write_to_file received invalid file_path_str: {file_path_str}")
            return False
        resolved_path = self._resolve_path(file_path_str)
        try:
            if create_dirs and not resolved_path.parent.exists():
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
                print(f"INFO: FileSystemTool: Created directory {resolved_path.parent}")
            
            str_content_lines = [str(line) for line in content_lines] # Ensure all lines are strings
            content_to_write = "\n".join(str_content_lines)
            if content_to_write and not content_to_write.endswith("\n"): # Ensure trailing newline if content exists
                content_to_write += "\n"
            
            resolved_path.write_text(content_to_write, encoding='utf-8')
            print(f"INFO: FileSystemTool: Successfully wrote to '{resolved_path}'")
            return True
        except Exception as e:
            print(f"ERROR: FileSystemTool: Could not write to file {resolved_path}: {e}")
            return False

class LLMTool:
    def __init__(self, config_data: dict):
        self.config_data = config_data
        self.openrouter_key = config_data.get("OPENROUTER_API_KEY")
        self.openrouter_site_url = config_data.get("OPENROUTER_SITE_URL")
        self.openrouter_app_name = config_data.get("OPENROUTER_REFERRER")
        self.ollama_base_url = config_data.get("OLLAMA_BASE_URL")
        self.default_model_choice = config_data.get("DEFAULT_MODEL_CHOICE")
        self.max_tokens_for_generation = int(config_data.get("MAX_TOKENS_GENERATION", 2048))
        
        self.openrouter_connector: OpenRouterConnector | None = None
        self.ollama_connector: OllamaConnector | None = None
        
        if self.openrouter_key:
            self.openrouter_connector = OpenRouterConnector(
                api_key=self.openrouter_key, site_url=self.openrouter_site_url, app_name=self.openrouter_app_name
            )
        if self.ollama_base_url or (self.default_model_choice and str(self.default_model_choice).startswith("ollama/")):
            self.ollama_base_url = self.ollama_base_url or "http://localhost:11434"
            self.ollama_connector = OllamaConnector(base_url=self.ollama_base_url)

    def _get_client_and_model(self, model_choice_str: str | None) -> tuple[OpenRouterConnector | OllamaConnector | None, str | None]:
        effective_model_choice = model_choice_str or self.default_model_choice
        if not effective_model_choice or not isinstance(effective_model_choice, str): # Added type check
            print("ERROR: LLMTool._get_client_and_model: No valid model choice provided or configured as default.")
            return None, None

        parts = effective_model_choice.split('/', 1)
        provider = parts[0].lower()
        model_name_from_parts = parts[1] if len(parts) > 1 else None

        if provider == "openrouter":
            if not self.openrouter_connector:
                print("ERROR: LLMTool: OpenRouter connector not initialized (API key likely missing).")
                return None, None
            # Use model_name_from_parts if present, otherwise it might be a model like "openrouter/mistralai/mistral-7b" where provider is the first part
            model_name_to_use = model_name_from_parts if model_name_from_parts else effective_model_choice # Fallback if malformed
            if not model_name_from_parts and provider == model_name_to_use : # e.g. "openrouter/openrouter" (unlikely but handles)
                 print(f"WARNING: OpenRouter model name not fully specified in '{effective_model_choice}'. Please use format 'openrouter/author/model'.")
                 return None, None
            return self.openrouter_connector, model_name_to_use
        
        elif provider == "ollama":
            if not self.ollama_connector:
                self.ollama_base_url = self.ollama_base_url or "http://localhost:11434"
                print(f"INFO: LLMTool: Initializing Ollama connector on demand with base_url: {self.ollama_base_url}")
                self.ollama_connector = OllamaConnector(base_url=self.ollama_base_url)
            model_name_to_use = model_name_from_parts or self.config_data.get("OLLAMA_DEFAULT_MODEL_NAME_ONLY", "mistral")
            return self.ollama_connector, model_name_to_use
        
        else: # Assume it's an Ollama model name directly
            print(f"WARNING: LLM provider for '{effective_model_choice}' not explicitly 'openrouter' or 'ollama'. Assuming Ollama model name: '{effective_model_choice}'.")
            if not self.ollama_connector:
                 self.ollama_base_url = self.ollama_base_url or self.config_data.get("OLLAMA_BASE_URL", "http://localhost:11434")
                 print(f"INFO: LLMTool: Initializing Ollama connector on demand (direct model name) with base_url: {self.ollama_base_url}")
                 self.ollama_connector = OllamaConnector(base_url=self.ollama_base_url)
            return self.ollama_connector, effective_model_choice

    def query_llm(self, prompt: str, model_choice: str, system_message: str = None, max_tokens: int | None = None, temperature=0.5) -> str:
        client, model_name = self._get_client_and_model(model_choice)
        if client is None or model_name is None:
            err_msg = f"Error: Could not get LLM client or model name for '{model_choice}'. Client: {client}, ModelName: {model_name}"
            print(f"ERROR: LLMTool.query_llm: {err_msg}")
            return err_msg
        
        effective_max_tokens = max_tokens if max_tokens is not None else self.max_tokens_for_generation
        
        try:
            # Ensure model_name passed to generate is just the name, not "provider/name" if client handles provider
            # However, OpenRouterConnector expects the full "author/model" string.
            # OllamaConnector expects just the model tag.
            # _get_client_and_model should return the correct form of model_name for the specific client.
            return client.generate(prompt, model_name, system_message, effective_max_tokens, temperature)
        except Exception as e:
            print(f"ERROR: LLMTool.query_llm: Exception during client.generate for {model_name} (using {model_choice}): {e}")
            # import traceback; traceback.print_exc() # Uncomment for deeper debug
            return f"Error: LLM query failed for {model_name}. Details: {str(e)}"

    def _extract_code_from_llm_response(self, llm_response: str) -> list[str]:
        if not llm_response: return []
        code_blocks = re.findall(r"```(?:[a-zA-Z0-9\-\_]*\n)?([\s\S]*?)```", llm_response, re.DOTALL)
        if code_blocks:
            full_code = "\n".join([block.strip('\n') for block in code_blocks])
            return full_code.splitlines()
        lines = llm_response.splitlines()
        cleaned_lines = []
        skip_patterns = [
            r"^\s*(here('s| is) the code|sure, (here is|this is)|okay,( i've generated| here is)).*:$",
            r"^\s*(this code snippet will|the following code|you can use this).*",
            r"^\s*(let me know if you need anything else|i hope this helps|feel free to ask).*", r"^\s*```\s*$",
        ]
        # If response has characteristics of code/JSON and not conversational, take it as is
        stripped_response = llm_response.strip()
        if (stripped_response.startswith(("{", "[", "<")) and stripped_response.endswith(("}", "]", ">"))) or \
           (not any(char.isalpha() for char in stripped_response[:10]) and any(char in "{[<()}]" for char in stripped_response[:20])): # Heuristic for code-like
            return lines

        for line in lines:
            if not any(re.match(p, line, re.IGNORECASE) for p in skip_patterns): cleaned_lines.append(line)
        
        if not cleaned_lines and llm_response.strip(): return [llm_response.strip()] 
        return cleaned_lines

    def generate_code_snippet(self, user_request: str, model_choice: str, original_code_snippet: str | None = None, surrounding_context: str | None = None) -> list[str]:
        system_message = "You are a precise code generation assistant... (same as before)"
        prompt = f"User Request: {user_request}\n\n"
        # ... (prompt construction as before) ...
        if original_code_snippet: prompt += f"Original Code Snippet (to be replaced/refactored):\n```\n{original_code_snippet}\n```\n\n"
        if surrounding_context: prompt += f"Surrounding Code Context (for style and reference, do not repeat this context in your output):\n```\n{surrounding_context}\n```\n\n"
        prompt += "New Code Snippet (output only the code, without any surrounding text or explanation):"

        generated_text = self.query_llm(prompt, model_choice, system_message=system_message, temperature=0.2)
        return self._extract_code_from_llm_response(generated_text)

    def generate_json_block_identifier(self, user_block_description: str, file_context_snippet: str, model_choice: str) -> dict | None:
        system_message = """You are an expert in identifying code blocks... (same as before)"""
        prompt = f"User's description of the code block: \"{user_block_description}\"\n" # ... (prompt construction as before)
        prompt += f"Snippet of the file content (for context):\n```\n{file_context_snippet}\n```\n"
        prompt += "Generate the JSON block identifier object (JSON only):"

        response_str = self.query_llm(prompt, model_choice, system_message=system_message, temperature=0.1, max_tokens=600) # Increased max_tokens
        
        if not response_str or response_str.startswith("Error:"):
            print(f"ERROR: LLMTool.generate_json_block_identifier: LLM query failed: {response_str}")
            return None

        response_str_cleaned = response_str.strip()
        # ... (cleaning and parsing logic as before) ...
        if response_str_cleaned.startswith("```json"): response_str_cleaned = response_str_cleaned[len("```json"):]
        if response_str_cleaned.startswith("```"): response_str_cleaned = response_str_cleaned[len("```"):]
        if response_str_cleaned.endswith("```"): response_str_cleaned = response_str_cleaned[:-len("```")]
        response_str_cleaned = response_str_cleaned.strip()
        try:
            parsed_json = json.loads(response_str_cleaned)
            if "type" not in parsed_json: raise ValueError("Generated JSON missing 'type' field.")
            print(f"INFO: LLM generated block identifier: {json.dumps(parsed_json, indent=2)}")
            return parsed_json
        except (json.JSONDecodeError, ValueError) as e:
            print(f"ERROR: LLM failed to generate valid JSON for block identifier. Error: {e}")
            print(f"LLM Response (cleaned) was:\n---\n{response_str_cleaned}\n---"); return None


    def generate_plan_step(self, current_state: 'StateManager') -> tuple[str | None, str | None]:
        planning_model = current_state.mode_config.get('planning_model', 'ollama/mistral:7b')
        
        system_prompt = """You are an AI assistant driving a ReAct loop.
Your goal is to complete sub-tasks for modifying code.
1. First, provide your 'thought' process (between 1-3 sentences) on how to achieve the current sub-task.
2. Second, based on your thought, output a JSON 'action' object for the next tool call.
   Action JSON format: {"tool_name": "ToolClass.method_name", "arguments": {"arg1": "val1", ...}}
   OR {"tool_name": "finish_sub_task", "result": {"status": "success" | "failure", "message": "...", "directives": [...]}}
   OR {"tool_name": "RequestClarificationTool.request_clarification", "arguments": {"question_for_user": "Your question"}}

Respond ONLY with the following structure, ensuring valid JSON for the action part:
Thought: [Your thought process here]
Action: [Your JSON action object here]

Do NOT include any other text before "Thought:" or after the "Action:" JSON. The Action JSON must be valid and complete.
Tool Argument Details:
- FileSystemTool.read_file: needs {"file_path_str": "relative/path/to/file.ext"}
- CodeAnalysisTool.get_code_structure: needs {"file_content": "content_string_from_cache", "file_type": "python|html|css|etc."}
- LLMTool.generate_code_snippet: needs {"user_request": "description...", "original_code_snippet": null_or_string, "surrounding_context": null_or_string}. 'model_choice' will be set by system.
- LLMTool.generate_multi_part_code_solution: needs {"user_request": "description...", "file_contexts": {"file1.ext": "context1_str_or_null", ...}}. 'model_choice' will be set by system.
- RequestClarificationTool.request_clarification: needs {"question_for_user": "Specific question..."}
- finish_sub_task: needs {"status": "success"|"failure", "message": "Reason...", "directives": [list_of_change_directives_if_success]}

Important Notes:
- Use `FileSystemTool.read_file` for ANY file you need content from, even if mentioned in `estimated_involved_files`. The `File Cache Summary` shows what's ALREADY read.
- If `File Cache Summary` shows a file's content, use that content for other tools (like `CodeAnalysisTool.get_code_structure` or as context for generation). Do not read it again unless necessary.
- Ensure all string values within the JSON action are properly quoted (e.g. "value"). File paths should be strings.
"""
        history_for_prompt = current_state.get_history_for_sub_task(current_state.current_sub_task_id)
        if len(history_for_prompt) > 2: history_for_prompt = history_for_prompt[-2:] # Limit history further
        
        file_cache_summary = {}
        for fp, content in current_state.file_cache.items():
            file_cache_summary[fp] = f"Exists in cache. Length: {len(content) if content else 0}. Snippet: {str(content)[:80]}..." if content else "Exists in cache (content is None - read failed or not found)."

        prompt = f"Overall Goal: {current_state.plan.get('overall_goal', 'N/A')}\n"
        prompt += f"Current Sub-task ID '{current_state.current_sub_task_id}': {current_state.get_current_sub_task_description()}\n"
        prompt += f"History for this sub-task (last {len(history_for_prompt)} steps): {json.dumps(history_for_prompt, indent=2)}\n"
        prompt += f"File Cache Summary: {json.dumps(file_cache_summary, indent=2)}\n"
        prompt += f"Available tools: [FileSystemTool.read_file, LLMTool.generate_code_snippet, LLMTool.generate_multi_part_code_solution, CodeAnalysisTool.get_code_structure, RequestClarificationTool.request_clarification, finish_sub_task]\n"
        prompt += "Provide your Thought and Action (Thought: ... Action: {JSON...}):"

        print(f"DEBUG LLMTool.generate_plan_step: Prompting {planning_model} for thought and action...")
        # print(f"--- Plan Step Prompt (to {planning_model}) ---\nSYSTEM:\n{system_prompt}\nUSER:\n{prompt}\n--- End Plan Step Prompt ---")
        
        response_text = self.query_llm(
            prompt, planning_model, system_message=system_prompt, 
            max_tokens=current_state.mode_config.get('max_tokens_generation', 1500), temperature=0.25 # Slightly lower temp
        )

        if not response_text or response_text.startswith("Error:"):
            print(f"ERROR: LLMTool.generate_plan_step: LLM query failed or returned error: {response_text}")
            return f"LLM query for plan step failed: {response_text}", None

        thought = "Could not parse thought."
        action_json_str = None # Initialize to None

        # Try to parse "Thought: ... Action: {JSON...}" structure
        # Make regex more robust to variations in whitespace and ensure DOTALL for thought
        thought_action_match = re.search(r"Thought:\s*(.*?)(?:\n\s*Action:\s*(\{[\s\S]*?\})\s*$|\Z)", response_text, re.DOTALL | re.IGNORECASE)

        if thought_action_match:
            thought = thought_action_match.group(1).strip()
            if thought_action_match.group(2): # If Action JSON part was captured
                action_json_str_candidate = thought_action_match.group(2).strip()
                # Attempt to fix common LLM JSON errors (e.g., missing trailing quote on last string value)
                action_json_str_candidate = re.sub(r'(:\s*"[^"]*?[^"\\])\s*(\}\s*)$', r'\1"\2', action_json_str_candidate)
                action_json_str_candidate = re.sub(r'(:\s*"[^"]*?[^"\\])\s*(,\s*".*)$', r'\1"\2', action_json_str_candidate)
                try:
                    json.loads(action_json_str_candidate) 
                    action_json_str = action_json_str_candidate # Valid JSON
                except json.JSONDecodeError as e:
                    print(f"ERROR: LLMTool.generate_plan_step: Action part looked like JSON but failed to parse: {e}")
                    print(f"Problematic Action JSON string from LLM (after attempted fix): {action_json_str_candidate}")
                    thought += f" (Self-correction note: Previous LLM Action was not valid JSON: '{action_json_str_candidate[:100]}...')"
                    # action_json_str remains None
        else: # Could not parse "Thought: ... Action: ..." structure, treat whole response as thought.
            thought = f"LLM Response (could not parse Thought/Action structure): {response_text}"
            print(f"WARNING: LLMTool.generate_plan_step: Could not parse standard Thought/Action structure. Full response treated as thought.")
            print(f"LLM Response for plan step was:\n{response_text}")


        print(f"LLMTool.generate_plan_step -> Thought: {thought}")
        print(f"LLMTool.generate_plan_step -> Action JSON str: {action_json_str if action_json_str else 'None (parsing failed or not provided by LLM)'}")
        return thought, action_json_str


    def generate_multi_part_code_solution(self, user_request: str, file_contexts: dict, model_choice: str) -> list:
        system_prompt = """You are an AI code generation assistant... (same as before, ensure JSON only, no markdown)"""
        # ... (prompt construction and LLM call as before, ensuring robust JSON parsing of the list of directives) ...
        # ... (cleaning and parsing logic for list of directives as before) ...
        prompt_parts = [f"User Request: {user_request}\n\nFile Contexts (relevant snippets from files already read, or indicate if a file is new):"]
        for fp, content in file_contexts.items():
            content_str = str(content) if content is not None else " (File is new or content not yet available)"
            prompt_parts.append(f"\n--- Context for: {fp} ---\n{content_str[:1500]}...\n--- END Context for: {fp} ---")
        
        llm_prompt = "\n".join(prompt_parts) + "\n\nGenerate the JSON array of change directives (JSON only, no markdown):"
        print(f"DEBUG LLMTool.generate_multi_part_code_solution: Prompting {model_choice}...")
        
        response_str = self.query_llm(llm_prompt, model_choice, system_message=system_prompt, temperature=0.2)

        if not response_str or response_str.startswith("Error:"):
            print(f"ERROR: LLMTool.generate_multi_part_code_solution: LLM query failed or returned error: {response_str}")
            return []

        response_str_cleaned = response_str.strip()
        if response_str_cleaned.startswith("```json"): response_str_cleaned = response_str_cleaned[len("```json"):]
        if response_str_cleaned.startswith("```"): response_str_cleaned = response_str_cleaned[len("```"):]
        if response_str_cleaned.endswith("```"): response_str_cleaned = response_str_cleaned[:-len("```")]
        response_str_cleaned = response_str_cleaned.strip()

        try:
            directives = json.loads(response_str_cleaned)
            if isinstance(directives, list):
                valid_directives = []
                for i, d in enumerate(directives):
                    if isinstance(d, dict) and "file_path" in d and "change_type" in d and "code_snippet" in d:
                        valid_directives.append(d)
                    else: print(f"WARNING: Directive {i} in multi-part solution has invalid structure, skipping: {d}")
                print(f"INFO: LLM generated {len(valid_directives)} valid multi-part directives.")
                return valid_directives
            else:
                print(f"ERROR: LLM did not return a list for multi-part solution. Response was:\n{response_str_cleaned}")
                return []
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse multi-part code solution JSON: {e}")
            print(f"LLM Response (cleaned) for multi-part was:\n---\n{response_str_cleaned}\n---"); return []


    def generate_clarification_question(self, current_state: 'StateManager', ambiguity_details: str, model_choice: str) -> str:
        prompt = f"The AI agent is trying to complete the sub-task: '{current_state.get_current_sub_task_description()}'.\n" # ... (as before)
        prompt += f"It encountered an ambiguity or needs more information: '{ambiguity_details}'.\n"
        prompt += f"History for this sub-task (last 2 steps): {json.dumps(current_state.get_history_for_sub_task(current_state.current_sub_task_id)[-2:], indent=2)}\n"
        prompt += "Formulate a clear, concise question for the user to resolve this ambiguity or provide the missing information. The question should guide the user to provide a specific answer."
        system_message = "You are an AI assistant. Generate ONLY the question for the user. Do not add any preamble like 'Okay, here is the question:'."
        
        print(f"DEBUG LLMTool.generate_clarification_question: Prompting {model_choice}...")
        question = self.query_llm(prompt, model_choice, system_message=system_message, max_tokens=250, temperature=0.4)
        
        if question.startswith("Error:"):
            print(f"WARNING: LLM failed to generate clarification question: {question}")
            return f"I need more details about: {ambiguity_details}. Can you please clarify specifically what I should do regarding this?"
        return question.strip()


class CodeAnalysisTool:
    # ... (No changes needed here from the previous full code listing for CodeAnalysisTool) ...
    def get_file_context_snippet(self, file_content: str, max_lines=50, max_chars=2000) -> str:
        lines = str(file_content).splitlines() 
        snippet_lines = lines[:max_lines]
        snippet_str = "\n".join(snippet_lines)
        return snippet_str[:max_chars]

    def get_code_structure(self, file_content: str, file_type: str) -> dict:
        print(f"INFO: CodeAnalysisTool.get_code_structure called for file_type: {file_type}")
        content_str = str(file_content) 

        if file_type == "python":
            functions = re.findall(r"^\s*def\s+(\w+)\s*\(", content_str, re.MULTILINE)
            classes = re.findall(r"^\s*class\s+(\w+)\s*[:\(]", content_str, re.MULTILINE)
            return {"type": "python", "functions": functions, "classes": classes, "summary": f"Found {len(functions)} functions, {len(classes)} classes (basic regex scan)."}
        elif file_type == "html":
            head_match = re.search(r"<head[^>]*>([\s\S]*?)</head>", content_str, re.IGNORECASE)
            body_match = re.search(r"<body[^>]*>([\s\S]*?)</body>", content_str, re.IGNORECASE)
            scripts = re.findall(r"<script[^>]*src=[\"']([^\"']+)[\"'][^>]*>", content_str, re.IGNORECASE)
            inline_scripts_count = len(re.findall(r"<script[^>]*>([\s\S]*?)</script>", content_str, re.IGNORECASE)) - len(scripts)
            structure = {"type": "html", "has_head": bool(head_match), "has_body": bool(body_match), "external_scripts": scripts, "inline_scripts_count": inline_scripts_count }
            return structure
        elif file_type == "css":
            rules_count = len(re.findall(r"([^{]+)\s*{[^}]+}", content_str))
            variables_count = len(re.findall(r"--[\w-]+:", content_str))
            return {"type": "css", "estimated_rules": rules_count, "css_variables_found": variables_count}
        
        return {"type": file_type, "summary": f"Basic structure analysis for '{file_type}'. First 200 chars: {content_str[:200]}..."}

    def extract_relevant_context(self, file_content: str, primary_target_identifier: dict, surrounding_lines: int = 10) -> str:
        print(f"INFO: CodeAnalysisTool.extract_relevant_context called (currently a placeholder). Target: {primary_target_identifier}")
        return str(file_content)[:1000]


class ChangeOrchestratorTool:
    # ... (No changes needed here from the previous full code listing for ChangeOrchestratorTool) ...
    def __init__(self):
        pass

    def apply_all_changes(self, 
                          all_directive_groups: list[list[dict]], 
                          fs_tool: FileSystemTool, 
                          replacer_core_module, 
                          state_manager: 'StateManager',
                          no_backup: bool
                          ) -> bool:
        print(f"INFO: ChangeOrchestratorTool.apply_all_changes called.")
        overall_success = True
        
        flat_directives = []
        if all_directive_groups and isinstance(all_directive_groups, list):
            for group in all_directive_groups:
                if group and isinstance(group, list): 
                    flat_directives.extend(d for d in group if isinstance(d, dict))

        if not flat_directives:
            print("INFO: ChangeOrchestratorTool: No valid directives to apply.")
            return True 

        changes_by_file = {}
        for directive in flat_directives:
            fp = directive.get("file_path")
            if not fp or not isinstance(fp, str):
                print(f"WARNING: Directive missing or has invalid 'file_path': {directive}")
                overall_success = False; continue
            if fp not in changes_by_file: changes_by_file[fp] = []
            changes_by_file[fp].append(directive)

        for file_path_str, directives_for_file in changes_by_file.items():
            resolved_file_path_for_log = fs_tool._resolve_path(file_path_str)
            print(f"\nProcessing changes for file: '{file_path_str}' (resolved: '{resolved_file_path_for_log}')")
            
            current_file_content_str = state_manager.get_file_from_cache(file_path_str)
            file_existed_on_disk_initially = resolved_file_path_for_log.exists() and resolved_file_path_for_log.is_file()

            if current_file_content_str is None: 
                if file_existed_on_disk_initially:
                    current_file_content_str = fs_tool.read_file(file_path_str) 
                    if current_file_content_str is None:
                        print(f"ERROR: Failed to read existing file '{resolved_file_path_for_log}'. Cannot apply changes to this file.")
                        overall_success = False; continue
                else: 
                    is_creation = any(d.get("change_type") == "create_or_replace_file" for d in directives_for_file)
                    if is_creation: current_file_content_str = ""
                    else:
                        print(f"WARNING: File '{resolved_file_path_for_log}' not found and not marked for creation. Assuming empty for ops.")
                        current_file_content_str = ""
            
            current_file_lines = current_file_content_str.splitlines()
            original_content_for_diff = current_file_content_str

            for i, directive in enumerate(directives_for_file):
                print(f"  Applying directive {i+1}/{len(directives_for_file)}: Type '{directive.get('change_type')}' to '{file_path_str}'")
                change_type = directive.get("change_type")
                code_snippet_lines = directive.get("code_snippet", [])
                if not isinstance(code_snippet_lines, list):
                    code_snippet_lines = str(code_snippet_lines).splitlines()

                if change_type == "create_or_replace_file": current_file_lines = code_snippet_lines
                elif change_type == "append_to_file": current_file_lines.extend(code_snippet_lines)
                elif change_type == "prepend_to_file": current_file_lines = code_snippet_lines + current_file_lines
                elif change_type == "replace_block":
                    block_id = directive.get("block_identifier")
                    if not block_id or not isinstance(block_id, dict):
                        print(f"  ERROR: 'replace_block' directive invalid 'block_identifier' for {file_path_str}. Directive: {directive}"); overall_success = False; continue
                    indent_handling = directive.get("indentation_handling", "match_original_block_start")
                    modified_lines = replacer_core_module.perform_replacement_on_content(
                        current_file_lines, block_id, code_snippet_lines, indent_handling, file_path_str
                    )
                    if modified_lines is not None: current_file_lines = modified_lines
                    else: print(f"  ERROR: 'replace_block' failed for {file_path_str}. Block ID type: '{block_id.get('type')}'."); overall_success = False
                
                elif change_type in ["insert_after_element", "insert_before_element"]:
                    target_selector = directive.get("target_element_selector")
                    if not target_selector or not isinstance(target_selector, str):
                        print(f"  ERROR: '{change_type}' directive invalid 'target_element_selector' for {file_path_str}"); overall_success = False; continue
                    
                    insertion_point_idx = -1
                    for line_idx, line_content in enumerate(current_file_lines):
                        if target_selector in line_content: insertion_point_idx = line_idx; break
                    
                    if insertion_point_idx != -1:
                        base_indent = replacer_core_module.get_indent_str(current_file_lines[insertion_point_idx])
                        indented_snippet = replacer_core_module.apply_indentation(code_snippet_lines, base_indent, "match_original_block_start")
                        if change_type == "insert_after_element":
                            current_file_lines = current_file_lines[:insertion_point_idx+1] + indented_snippet + current_file_lines[insertion_point_idx+1:]
                        else: 
                            current_file_lines = current_file_lines[:insertion_point_idx] + indented_snippet + current_file_lines[insertion_point_idx:]
                    else:
                        print(f"  WARNING: Target selector '{target_selector}' for '{change_type}' not found in {file_path_str}. Appending snippet to end of file instead.")
                        current_file_lines.extend(code_snippet_lines)
                else:
                    print(f"  WARNING: Unknown change_type '{change_type}' for {file_path_str}. Skipping directive."); overall_success = False
            
            modified_file_content_str = "\n".join(current_file_lines)
            if modified_file_content_str and not modified_file_content_str.endswith("\n"): modified_file_content_str += "\n"

            if state_manager.dry_run:
                print(f"\n--- Dry Run: Proposed changes for {resolved_file_path_for_log} ---")
                if original_content_for_diff.strip() == modified_file_content_str.strip() and original_content_for_diff != modified_file_content_str :
                     print("INFO: Content changed (likely whitespace/line endings only).")
                elif original_content_for_diff == modified_file_content_str:
                     print("INFO: No effective changes proposed by diff for this file.")
                else: replacer_core_module.show_diff(original_content_for_diff, modified_file_content_str, file_path_str)
            else:
                if not no_backup and file_existed_on_disk_initially: 
                    replacer_core_module.backup_file(resolved_file_path_for_log)
                
                write_success = fs_tool.write_to_file(file_path_str, current_file_lines, create_dirs=True)
                if write_success:
                    print(f"  ✅ Successfully wrote modifications to '{resolved_file_path_for_log}'.")
                    state_manager.update_file_cache(file_path_str, modified_file_content_str)
                else:
                    print(f"  ❌ Failed to write modifications to '{resolved_file_path_for_log}'."); overall_success = False
        return overall_success