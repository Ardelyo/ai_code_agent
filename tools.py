# tools.py
import json
import re
from pathlib import Path
from connectors import OpenRouterConnector, OllamaConnector # Assuming connectors.py is in the same dir or PYTHONPATH

class FileSystemTool:
    def read_file(self, file_path_str: str) -> str | None:
        file_path = Path(file_path_str)
        try:
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                print(f"INFO: Read file '{file_path}' ({len(content)} chars).")
                return content
            else:
                print(f"ERROR: File not found for reading: {file_path}")
                return None
        except Exception as e:
            print(f"ERROR: Could not read file {file_path}: {e}")
            return None

    def write_to_file(self, file_path_str: str, content_lines: list[str], create_dirs: bool = True):
        file_path = Path(file_path_str)
        try:
            if create_dirs and not file_path.parent.exists() and str(file_path.parent) != ".":
                file_path.parent.mkdir(parents=True, exist_ok=True)
                print(f"INFO: Created directory {file_path.parent}")
            
            file_path.write_text("\n".join(content_lines) + "\n", encoding='utf-8')
            print(f"INFO: Successfully wrote to '{file_path}'")
            return True
        except Exception as e:
            print(f"ERROR: Could not write to file {file_path}: {e}")
            return False

class LLMTool:
    def __init__(self, config_data: dict):
        self.config_data = config_data
        self.openrouter_key = config_data.get("OPENROUTER_API_KEY")
        self.openrouter_site_url = config_data.get("OPENROUTER_SITE_URL")
        self.openrouter_app_name = config_data.get("OPENROUTER_REFERRER")
        self.ollama_base_url = config_data.get("OLLAMA_BASE_URL")
        
        self.openrouter_connector = None
        self.ollama_connector = None
        
        if self.openrouter_key:
            self.openrouter_connector = OpenRouterConnector(
                api_key=self.openrouter_key,
                site_url=self.openrouter_site_url,
                app_name=self.openrouter_app_name
            )
        
        # Only initialize Ollama connector if we're actually using Ollama
        default_model = config_data.get("DEFAULT_MODEL_CHOICE", "").lower()
        if default_model.startswith("ollama/") or self.ollama_base_url:
            if not self.ollama_base_url:
                self.ollama_base_url = "http://localhost:11434"
            self.ollama_connector = OllamaConnector(base_url=self.ollama_base_url)

    def _get_client_and_model(self, model_choice_str: str) -> tuple[any, str]:
        parts = model_choice_str.split('/', 1)
        provider = parts[0].lower()
        model_name = parts[1] if len(parts) > 1 else None

        if provider == "openrouter":
            if not self.openrouter_connector:
                raise ValueError("OpenRouter API key not configured, cannot use OpenRouter models.")
            if not model_name:
                raise ValueError("Model name required for OpenRouter (e.g., openrouter/mistralai/mistral-7b-instruct)")
            return self.openrouter_connector, model_name
        elif provider == "ollama":
            if not model_name: # Use default if configured, or raise error
                model_name = self.config_data.get("OLLAMA_DEFAULT_MODEL")
                if not model_name:
                    raise ValueError("Model name required for Ollama (e.g., ollama/llama3 or configure OLLAMA_DEFAULT_MODEL)")
            return self.ollama_connector, model_name
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}. Supported: openrouter, ollama.")

    def query_llm(self, prompt: str, model_choice_str: str, system_message: str = None, max_tokens=2048, temperature=0.5) -> str:
        try:
            client, model_name = self._get_client_and_model(model_choice_str)
            return client.generate(prompt, model_name, system_message, max_tokens, temperature)
        except ValueError as ve: # Catch config errors from _get_client_and_model
            print(f"ERROR: {ve}")
            return f"Error: Configuration problem for model {model_choice_str}."
        except Exception as e:
            print(f"ERROR: LLM query failed unexpectedly for model {model_choice_str}: {e}")
            return f"Error: LLM query failed for {model_choice_str}."


    def generate_code_snippet(self, user_request: str, original_code_snippet: str | None, surrounding_context: str | None, model_choice: str) -> list[str]:
        system_message = "You are a precise code generation assistant. Given a user request, and optionally an original code snippet to be replaced/refactored and some surrounding context, generate ONLY the new code snippet. Adhere to the language and style of the provided context if possible. Do not include explanations, apologies, or any text other than the code itself. If the request is to delete, output an empty string or a comment indicating deletion."
        
        prompt = f"User Request: {user_request}\n\n"
        if original_code_snippet:
            prompt += f"Original Code Snippet (to be replaced/refactored):\n```\n{original_code_snippet}\n```\n\n"
        if surrounding_context:
            prompt += f"Surrounding Code Context (for style and reference, do not repeat this context in your output):\n```\n{surrounding_context}\n```\n\n"
        prompt += "New Code Snippet (output only the code):"
        
        generated_text = self.query_llm(prompt, model_choice, system_message=system_message, max_tokens=3000, temperature=0.3)
        return self._extract_code_from_llm_response(generated_text)

    def generate_json_block_identifier(self, user_block_description: str, file_context_snippet: str, model_choice: str) -> dict | None:
        system_message = """You are an expert in identifying code blocks based on descriptions.
Your task is to generate a JSON object that precisely describes how to find a code block.
The JSON must have a "type" field, which can be "function_name", "class_name", or "custom_markers".

If "type" is "function_name" or "class_name":
  - Include a "name" field with the exact function or class name.
  - Optionally include "definition_line_only": true if only the def/class line should be targeted.

If "type" is "custom_markers":
  - Include "start_marker_regex": a Python regex string to match the entire start marker line (e.g., "^\\\\s*# START_BLOCK\\\\s*$").
  - Include "end_marker_regex": a Python regex string to match the entire end marker line.
  - Optionally include "inclusive_markers": true if markers are part of the block.

Respond ONLY with the valid JSON object. Do not include any other text or explanations.
"""
        prompt = f"User's description of the code block: \"{user_block_description}\"\n\n"
        prompt += f"Snippet of the file content (for context):\n```\n{file_context_snippet}\n```\n\n"
        prompt += "Generate the JSON block identifier object:"

        response_str = self.query_llm(prompt, model_choice, system_message=system_message, temperature=0.1, max_tokens=500)
        
        # Try to extract JSON from markdown code block if present
        json_match = re.search(r"```json\s*([\s\S]*?)\s*```", response_str, re.DOTALL)
        if json_match:
            response_str = json_match.group(1).strip()
        else: # Try to find JSON that isn't in a markdown block
            json_match_plain = re.search(r"{\s*[\s\S]*?\s*}", response_str, re.DOTALL)
            if json_match_plain:
                response_str = json_match_plain.group(0).strip()
            else: # As a last resort, strip and hope it's just JSON
                 response_str = response_str.strip()


        try:
            parsed_json = json.loads(response_str)
            # Basic validation of the generated JSON
            if "type" not in parsed_json:
                raise ValueError("Generated JSON missing 'type' field.")
            print(f"INFO: LLM generated block identifier: {parsed_json}")
            return parsed_json
        except json.JSONDecodeError as e:
            print(f"ERROR: LLM failed to generate valid JSON for block identifier. Error: {e}")
            print(f"LLM Response was:\n---\n{response_str}\n---")
            return None
        except ValueError as ve:
            print(f"ERROR: Generated JSON for block identifier is invalid: {ve}")
            print(f"LLM Response was:\n---\n{response_str}\n---")
            return None

    def _extract_code_from_llm_response(self, llm_response: str) -> list[str]:
        # Try to find code blocks (e.g., ```python ... ``` or other languages)
        code_blocks = re.findall(r"```(?:[a-zA-Z0-9\-\_]*\n)?([\s\S]*?)```", llm_response, re.DOTALL)
        if code_blocks:
            # Join all found code blocks, then split into lines
            full_code = "\n".join([block.strip() for block in code_blocks])
            return full_code.splitlines()
        
        # Fallback: if no markdown code blocks, assume the whole response might be code,
        # but be cautious and try to clean it.
        # This part might need more sophisticated cleaning based on LLM habits.
        lines = llm_response.splitlines()
        # Remove potential intro/outro lines if they don't look like code
        cleaned_lines = []
        for line in lines:
            # A very simple heuristic: if a line looks like an explanation, skip it.
            # This is naive and might remove valid single-line comments that start sentences.
            # if not (line.strip().startswith("Here's the") or line.strip().startswith("Sure, this is")):
            cleaned_lines.append(line)
        
        if not cleaned_lines and llm_response.strip(): # If cleaning removed everything but original was not empty
            return [llm_response.strip()] # Return the stripped original as a single line
        elif not cleaned_lines:
            return [] # Truly empty
            
        return cleaned_lines

# CodeAnalysisTool can be basic for now, or integrated with find_target_block
class CodeAnalysisTool:
    def get_file_context_snippet(self, file_content: str, max_lines=50, max_chars=2000) -> str:
        lines = file_content.splitlines()
        snippet_lines = lines[:max_lines]
        snippet_str = "\n".join(snippet_lines)
        return snippet_str[:max_chars]