# advanced_planner_tools.py
import json
from pathlib import Path

class StateManager:
    def __init__(self, user_prompt: str, operational_mode: str, mode_config: dict,
                 project_base_path: Path, 
                 dry_run: bool):
        self.user_prompt = user_prompt
        self.operational_mode = operational_mode
        self.mode_config = mode_config 
        self.project_base_path = project_base_path
        self.dry_run = dry_run
        
        self.plan: dict | None = None
        self.current_sub_task_id: str | int | None = None
        self.history_per_sub_task: dict[str, list] = {} 
        self.file_cache: dict[str, str | None] = {} # Value can be None if read failed
        self.openrouter_api_calls_made_total: int = 0
        self.planning_iterations_current_sub_task: int = 0
        self.collected_change_directives: list[list[dict]] = [] 

        print(f"DEBUG StateManager: Initialized with mode_config: {json.dumps(self.mode_config, indent=2)}")
        print(f"DEBUG StateManager: Project Base Path: {self.project_base_path.resolve() if self.project_base_path else 'Not Set'}")

    def set_plan(self, plan_dict: dict | None):
        self.plan = plan_dict
        if self.plan:
            print(f"DEBUG StateManager: Plan set: {json.dumps(self.plan, indent=2)}")
        else:
            print("DEBUG StateManager: Plan set to None.")


    def get_current_sub_task_description(self) -> str:
        if self.plan and self.plan.get("sub_tasks") and self.current_sub_task_id is not None:
            for task in self.plan["sub_tasks"]:
                if task.get("id") == self.current_sub_task_id:
                    return task.get("description", "No description for this sub-task.")
        return "N/A - No current sub-task identified or plan not set."

    def add_history(self, sub_task_id: int | str, thought: str | None, action: dict | str | None, observation: dict):
        sub_task_id_key = str(sub_task_id)
        if sub_task_id_key not in self.history_per_sub_task:
            self.history_per_sub_task[sub_task_id_key] = []
        
        action_to_store = action
        if isinstance(action, str):
            action_to_store = {"raw_unparsed_action": action}
        elif action is None: # Handle None action
            action_to_store = {"error": "Action was None"}


        self.history_per_sub_task[sub_task_id_key].append({
            "thought": thought or "No thought recorded.", # Handle None thought
            "action": action_to_store, 
            "observation": observation 
        })
        action_name = action_to_store.get('tool_name', 'N/A') if isinstance(action_to_store, dict) else str(action_to_store)[:30]
        obs_summary = str(observation)[:70] + "..." if len(str(observation)) > 70 else str(observation)
        # print(f"DEBUG StateManager: History added for sub-task {sub_task_id_key}: T:{str(thought)[:30]}... A:{action_name} O:{obs_summary}")

    def get_history_for_sub_task(self, sub_task_id: int | str) -> list:
        return self.history_per_sub_task.get(str(sub_task_id), [])

    def update_file_cache(self, file_path: str, content: str | None): # Content can be None if read fails
        self.file_cache[file_path] = content
        if content is not None:
            print(f"DEBUG StateManager: File cache updated for '{file_path}' ({len(content)} chars)")
        else:
            print(f"DEBUG StateManager: File cache updated for '{file_path}' (content is None - e.g. read failed or file not found)")


    def get_file_from_cache(self, file_path: str) -> str | None:
        return self.file_cache.get(file_path)

    def increment_api_calls(self, provider_model_str=""):
        effective_provider = ""
        if provider_model_str and isinstance(provider_model_str, str) and '/' in provider_model_str:
            effective_provider = provider_model_str.split('/')[0].lower()
        elif provider_model_str: # Assume it might be a direct ollama model name
            effective_provider = "ollama" 

        if effective_provider == "openrouter":
            self.openrouter_api_calls_made_total += 1
            print(f"DEBUG StateManager: Total OpenRouter API calls: {self.openrouter_api_calls_made_total}/{self.mode_config.get('max_api_calls_openrouter', 'N/A')}")
        
        # This counter is for sub-task iterations, regardless of provider for the specific call
        # but primarily limited by ollama_iterations config or openrouter_calls if that's the planning provider
        self.planning_iterations_current_sub_task += 1
        # Determine the relevant limit for logging current sub-task iterations
        iter_limit_key = 'max_planning_iterations_ollama'
        if effective_provider == 'openrouter' : # If current planning model is OR, its total limit is also a factor
             iter_limit_key = 'max_api_calls_openrouter' # Log against this as the iteration "cap"

        iter_limit_val = self.mode_config.get(iter_limit_key, 'N/A')
        print(f"DEBUG StateManager: Planning iterations for current sub-task (planner: {provider_model_str}): {self.planning_iterations_current_sub_task}/{iter_limit_val}")


    def check_api_limit_reached(self, provider_model_str="") -> bool:
        # Check total OpenRouter calls limit first, as it's a hard cap for the whole run
        or_limit_val = self.mode_config.get('max_api_calls_openrouter')
        if or_limit_val is not None and isinstance(or_limit_val, int) and self.openrouter_api_calls_made_total >= or_limit_val:
            print("WARNING: Total OpenRouter API call limit reached for this user request.")
            return True
        
        # Then check per-sub-task iteration limit
        # This limit applies more directly to Ollama or as a general safeguard against loops for any provider
        sub_task_iter_limit_val = self.mode_config.get('max_planning_iterations_ollama')
        if sub_task_iter_limit_val is not None and isinstance(sub_task_iter_limit_val, int) and self.planning_iterations_current_sub_task >= sub_task_iter_limit_val:
            print(f"WARNING: Per-sub-task planning iteration limit ({sub_task_iter_limit_val}) reached.")
            return True
            
        return False
    
    def add_change_directives_for_sub_task(self, directives: list | None): # Directives can be None
        if directives and isinstance(directives, list): 
            self.collected_change_directives.append(directives)
            print(f"DEBUG StateManager: Added {len(directives)} directives from sub-task. Total groups: {len(self.collected_change_directives)}")
        elif directives is None:
            print(f"DEBUG StateManager: No directives provided for current sub-task completion (directives was None).")
        else: # Not a list
             print(f"WARNING StateManager: Attempted to add non-list directives: {directives}")


    def get_full_path(self, relative_or_absolute_path: str) -> Path:
        if not self.project_base_path:
            print("CRITICAL WARNING: StateManager.project_base_path is not set. Attempting to use current directory as fallback.")
            return Path(relative_or_absolute_path).resolve() # Resolve relative to CWD if base_path is missing
        
        # Ensure relative_or_absolute_path is a string
        path_input_str = str(relative_or_absolute_path)
        given_path = Path(path_input_str)

        if given_path.is_absolute():
            return given_path.resolve()
        return (self.project_base_path / given_path).resolve()


class TaskDecomposer:
    def __init__(self, llm_tool, state_manager: StateManager):
        self.llm_tool = llm_tool
        self.state = state_manager

    def decompose(self) -> dict | None:
        print("INFO: TaskDecomposer.decompose() called.")
        
        planning_model = self.state.mode_config.get('planning_model', 'ollama/mistral:7b')
        print(f"DEBUG TaskDecomposer: Using planning model: {planning_model} for decomposition.")
        
        USE_ACTUAL_LLM_FOR_DECOMPOSITION = False # SET TO True TO ENABLE LLM DECOMPOSITION

        if not USE_ACTUAL_LLM_FOR_DECOMPOSITION:
            print("INFO: TaskDecomposer: Using DUMMY plan generation logic.")
            overall_goal_display = self.state.user_prompt.replace('\n', ' ').replace('\r', '')

            if "dark mode" in self.state.user_prompt.lower() or "light mode" in self.state.user_prompt.lower():
                plan_dict_content = {
                    "overall_goal": f"Implement theme toggle for the website, based on: {overall_goal_display}",
                    "estimated_involved_files": ["index.html", "style.css", "script.js"],
                    "sub_tasks": [
                        {"id": "html_button_task", "description": "Add HTML for the theme toggle button in index.html.", "complexity": "simple", "status": "pending"},
                        {"id": "css_theme_task", "description": "Define CSS for light/dark themes and style the toggle button in style.css.", "complexity": "medium", "status": "pending"},
                        {"id": "js_logic_task", "description": "Implement JavaScript logic in script.js for theme switching and persistence.", "complexity": "medium", "status": "pending"}
                    ]
                }
            else:
                plan_dict_content = {
                    "overall_goal": self.state.user_prompt,
                    "estimated_involved_files": [],
                    "sub_tasks": [
                        {"id": f"main_task_0_{Path(self.state.user_prompt[:20]).stem}", "description": self.state.user_prompt, "complexity": "unknown", "status": "pending"}
                    ]
                }
            plan_str_for_parsing = json.dumps(plan_dict_content, indent=2)
        else: 
            print(f"INFO: TaskDecomposer: Making ACTUAL LLM call to {planning_model} for plan decomposition.")
            self.state.increment_api_calls(planning_model)
            system_prompt = """You are an expert project planner. Given a user's request for code modification,
break it down into a logical sequence of sub-tasks. Each sub-task MUST have a unique string 'id'.
Identify any files likely to be involved for the overall goal.
For each sub-task, estimate its complexity (simple, medium, complex).
Respond ONLY with a valid JSON object containing:
{
  "overall_goal": "User's main goal summarized",
  "estimated_involved_files": ["file1.py", "file2.html"],
  "sub_tasks": [
    {"id": "unique_alphanumeric_step_1_id", "description": "Detailed step 1", "complexity": "simple", "status": "pending"},
    {"id": "unique_alphanumeric_step_2_id", "description": "Detailed step 2", "complexity": "medium", "status": "pending"}
  ]
}
Ensure the 'id' fields are unique strings. Do not include any text outside the JSON object.
"""
            user_llm_prompt = f"User request: \"{self.state.user_prompt}\"\n\nGenerate the JSON plan based on this request."
            plan_str_for_parsing = self.llm_tool.query_llm(user_llm_prompt, planning_model, system_message=system_prompt, max_tokens=1500)
            if not plan_str_for_parsing or plan_str_for_parsing.startswith("Error:"):
                print(f"ERROR: TaskDecomposer LLM call failed: {plan_str_for_parsing}")
                return None
        
        print(f"DEBUG TaskDecomposer: Plan string to be parsed by json.loads():\n{plan_str_for_parsing}")
        try:
            # Attempt to clean the string if it's not perfect JSON (e.g. remove markdown fences)
            cleaned_plan_str = plan_str_for_parsing.strip()
            if cleaned_plan_str.startswith("```json"): cleaned_plan_str = cleaned_plan_str[len("```json"):]
            if cleaned_plan_str.startswith("```"): cleaned_plan_str = cleaned_plan_str[len("```"):]
            if cleaned_plan_str.endswith("```"): cleaned_plan_str = cleaned_plan_str[:-len("```")]
            cleaned_plan_str = cleaned_plan_str.strip()

            plan = json.loads(cleaned_plan_str)
            if not isinstance(plan, dict) or "sub_tasks" not in plan or not isinstance(plan["sub_tasks"], list):
                print("ERROR: TaskDecomposer: Parsed plan has invalid structure (e.g., missing 'sub_tasks' list)."); return None
            
            seen_ids = set()
            for i, task in enumerate(plan["sub_tasks"]):
                if not isinstance(task, dict): # Ensure each task is a dict
                    print(f"ERROR: TaskDecomposer: Sub-task at index {i} is not a dictionary. Task: {task}"); return None
                task_id = task.get("id")
                if not task_id or not isinstance(task_id, str) or task_id in seen_ids : 
                    # Generate more robust unique ID
                    desc_stem = Path(task.get('description','no_desc')[:20].replace(" ","_")).stem
                    task["id"] = f"generated_task_{i}_{desc_stem}"
                seen_ids.add(task["id"])
                task.setdefault("status", "pending")
                task.setdefault("complexity", "unknown") # Ensure complexity exists
            return plan
        except json.JSONDecodeError as e:
            print(f"ERROR: TaskDecomposer failed to parse JSON plan: {e}\nContent that failed parsing:\n---\n{plan_str_for_parsing}\n---"); return None


class ReActPlannerExecutor:
    def __init__(self, llm_tool, state_manager: StateManager, available_tools: dict, clarification_module):
        self.llm_tool = llm_tool
        self.state = state_manager
        self.tools = available_tools
        self.clarification_module = clarification_module

    def execute_plan(self) -> list[list[dict]]: # Returns list of (groups of) directives
        if not self.state.plan or not self.state.plan.get("sub_tasks"):
            print("ERROR: ReActPlannerExecutor: No plan or sub-tasks to execute.")
            return []

        all_sub_task_directives_groups = []

        for i, sub_task in enumerate(self.state.plan["sub_tasks"]):
            sub_task_id = sub_task.get("id", f"sub_task_index_{i}")
            self.state.current_sub_task_id = sub_task_id
            self.state.planning_iterations_current_sub_task = 0 
            print(f"\n>>> Executing Sub-task ID '{self.state.current_sub_task_id}': {sub_task.get('description')} <<<")

            planning_model_str = self.state.mode_config.get('planning_model', '')
            max_iterations = self.state.mode_config.get('max_planning_iterations_ollama', 10) # Default per-sub-task iter limit

            current_iteration = 0
            sub_task_completed_successfully = False
            directives_for_this_sub_task = []


            while current_iteration < max_iterations and not sub_task_completed_successfully:
                current_iteration += 1
                print(f"\n-- Sub-task ID '{self.state.current_sub_task_id}', Iteration {current_iteration}/{max_iterations} --")

                if self.state.check_api_limit_reached(planning_model_str): # Checks both OR total and sub-task iter
                    print(f"INFO: API/Iteration limit reached for sub-task '{self.state.current_sub_task_id}'. Stopping this sub-task.")
                    break
                
                thought_text, action_json_str = self.llm_tool.generate_plan_step(self.state)
                self.state.increment_api_calls(planning_model_str)

                if not action_json_str: # Error from generate_plan_step
                    print(f"ERROR: LLM failed to generate a valid action JSON for sub-task '{self.state.current_sub_task_id}'. Thought: '{thought_text}'. Skipping iteration.")
                    observation_data = {"status": "error", "message": "LLM failed to generate valid action JSON."}
                    self.state.add_history(self.state.current_sub_task_id, thought_text, {"error": "LLM action_json was None"}, observation_data)
                    continue
                
                try:
                    action_data = json.loads(action_json_str)
                    if not isinstance(action_data, dict): raise json.JSONDecodeError("Action is not a JSON object", action_json_str, 0)
                except json.JSONDecodeError as e:
                    print(f"ERROR: Could not parse LLM action JSON: '{action_json_str}'. Error: {e}")
                    observation_data = {"status": "error", "message": f"Failed to parse LLM action JSON: {e}"}
                    self.state.add_history(self.state.current_sub_task_id, thought_text, {"error": "parse failed", "raw_action": action_json_str}, observation_data)
                    continue

                tool_name_str = action_data.get("tool_name")
                tool_args = action_data.get("arguments", {}) if isinstance(action_data.get("arguments"), dict) else {} # Ensure args is a dict
                observation_data = {"status": "error", "message": f"Initial error: Unknown tool or action: '{tool_name_str}'"}

                if tool_name_str == "finish_sub_task":
                    print(f"INFO: Sub-task ID '{self.state.current_sub_task_id}' marked as finished by LLM.")
                    sub_task_completed_successfully = True 
                    task_result = action_data.get("result", {})
                    current_status = task_result.get("status", "success") # Assume success if not specified
                    observation_data = {"status": current_status, "message": task_result.get("message", "Sub-task completed.")}
                    
                    # Collect directives if present and task was successful
                    if current_status == "success" and "directives" in task_result and isinstance(task_result["directives"], list):
                        directives_for_this_sub_task.extend(task_result["directives"])
                    
                    for st_idx, st_val in enumerate(self.state.plan["sub_tasks"]):
                        if st_val.get("id") == self.state.current_sub_task_id:
                            self.state.plan["sub_tasks"][st_idx]["status"] = "completed" if current_status == "success" else "failed"
                            break
                
                elif tool_name_str == "RequestClarificationTool.request_clarification":
                    clarification_tool_instance = self.tools.get("RequestClarificationTool")
                    if clarification_tool_instance:
                        question_for_user = tool_args.get("question_for_user", "I need more details to proceed.")
                        observation_data = clarification_tool_instance.request_clarification(question_for_user=question_for_user)
                    else: observation_data = {"status": "error", "message": "RequestClarificationTool not found."}

                elif tool_name_str and '.' in tool_name_str :
                    try:
                        target_tool_class_name, target_method_name = tool_name_str.split('.', 1)
                        if target_tool_class_name in self.tools:
                            tool_instance = self.tools[target_tool_class_name]
                            if hasattr(tool_instance, target_method_name):
                                method_to_call = getattr(tool_instance, target_method_name)
                                print(f"Attempting to execute: {tool_name_str} with args: {json.dumps(tool_args, indent=2)}")

                                if isinstance(tool_instance, self.llm_tool.__class__): # If it's an LLMTool call
                                    # Always inject/override model_choice for generation, do NOT let LLM planner dictate it
                                    if "generate_code_snippet" in target_method_name or \
                                       "generate_multi_part_code_solution" in target_method_name:
                                        tool_args['model_choice'] = self.state.mode_config.get('generation_model')
                                        print(f"INFO: Set/Overrode model_choice to '{tool_args['model_choice']}' for {target_method_name}")
                                    # For other LLMTool methods, model is usually passed or comes from planning_model in method itself
                                
                                result = method_to_call(**tool_args)
                                observation_data = {"status": "success", "tool_output": result}
                                
                                if tool_name_str == "FileSystemTool.read_file": # Special handling for read_file observation
                                    if result is not None:
                                        self.state.update_file_cache(tool_args.get("file_path_str"), result)
                                        observation_data["message"] = f"File '{tool_args.get('file_path_str')}' read successfully."
                                    else: # File not found or read error
                                        observation_data["status"] = "error" # Mark observation as error
                                        observation_data["message"] = f"File '{tool_args.get('file_path_str')}' not found or could not be read."
                                        self.state.update_file_cache(tool_args.get("file_path_str"), None) # Cache the failure

                                elif tool_name_str == "LLMTool.generate_multi_part_code_solution" and isinstance(result, list):
                                    observation_data["directives_generated"] = result # For planner's context in next step
                                elif tool_name_str == "LLMTool.generate_code_snippet" and isinstance(result, list):
                                    observation_data["generated_snippet"] = result # For planner's context

                            else: observation_data = {"status": "error", "message": f"Method '{target_method_name}' not found in tool '{target_tool_class_name}'."}
                        else: observation_data = {"status": "error", "message": f"Tool class '{target_tool_class_name}' not found."}
                    except Exception as e:
                        print(f"CRITICAL ERROR executing tool {tool_name_str}: {e}")
                        import traceback; traceback.print_exc()
                        observation_data = {"status": "error", "message": f"Tool execution failed: {str(e)}"}
                else: observation_data = {"status": "error", "message": f"Invalid or missing tool_name format: '{tool_name_str}' (must be ToolClass.method_name)"}
                
                self.state.add_history(self.state.current_sub_task_id, thought_text, action_data, observation_data)
                if observation_data.get("status") == "error":
                    print(f"WARNING: Error in iteration for sub-task '{self.state.current_sub_task_id}', observation: {observation_data.get('message')}")

            # After sub-task loop finishes (completed or max iterations)
            if directives_for_this_sub_task: # If this sub-task produced directives
                all_sub_task_directives_groups.append(directives_for_this_sub_task)
            
            if not sub_task_completed_successfully:
                print(f"WARNING: Sub-task ID '{self.state.current_sub_task_id}' did not complete successfully within {max_iterations} iterations.")
                for st_idx, st_val in enumerate(self.state.plan["sub_tasks"]):
                    if st_val.get("id") == self.state.current_sub_task_id:
                        self.state.plan["sub_tasks"][st_idx]["status"] = "failed"
                        break
        
        self.state.current_sub_task_id = None
        return all_sub_task_directives_groups


class ClarificationModule:
    def __init__(self, state_manager: StateManager):
        self.state = state_manager

    def _ask_user_interaction(self, question_text: str) -> str:
        current_task_id_display = self.state.current_sub_task_id if self.state.current_sub_task_id is not None else 'N/A'
        print(f"\n🤔 AI Clarification Request (Sub-task ID '{current_task_id_display}'):")
        print(f"{question_text}")
        user_response = ""
        try:
            user_response = input("Your response: ").strip()
        except KeyboardInterrupt:
            print("\nUser cancelled clarification.")
            user_response = "User cancelled." # Or some other indicator
        return user_response
    
    def request_clarification(self, question_for_user: str) -> dict:
        if self.state.mode_config.get("allow_clarification_loops", False):
            user_answer = self._ask_user_interaction(question_for_user)
            if user_answer == "User cancelled.":
                return {"status": "clarification_cancelled_by_user", "user_response": user_answer}
            return {"status": "user_clarification_provided", "user_response": user_answer}
        else:
            print("INFO: Clarification skipped as per mode configuration.")
            return {"status": "clarification_skipped", "message": "Clarification loop disabled by mode."}