# connectors.py
import requests
import json
import os

class OpenRouterConnector:
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1", site_url: str = None, app_name: str = "AICodeAgent"):
        if not api_key:
            raise ValueError("OpenRouter API key is required.")
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if site_url:
            self.headers["HTTP-Referer"] = site_url
        if app_name:
            self.headers["X-Title"] = app_name

    def generate(self, prompt: str, model: str, system_message: str = None, max_tokens=2048, temperature=0.5) -> str:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model, # e.g., "mistralai/mistral-7b-instruct-v0.2"
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        try:
            print(f"INFO: Querying OpenRouter model: {model}...")
            response = requests.post(f"{self.base_url}/chat/completions", headers=self.headers, json=data, timeout=180)
            response.raise_for_status()
            response_json = response.json()
            content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"INFO: OpenRouter response received.")
            return content
        except requests.exceptions.RequestException as e:
            err_msg = f"ERROR: OpenRouter API request failed: {e}"
            if hasattr(e, 'response') and e.response is not None:
                err_msg += f" - Status: {e.response.status_code} - Body: {e.response.text[:500]}"
            print(err_msg)
            return f"Error: OpenRouter request failed. {e}"
        except (KeyError, IndexError) as e:
            print(f"ERROR: Could not parse OpenRouter response: {e} - Response: {response_json if 'response_json' in locals() else 'No JSON response'}")
            return "Error: Invalid response from OpenRouter."


class OllamaConnector:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')

    def generate(self, prompt: str, model: str, system_message: str = None, max_tokens=2048, temperature=0.5, stream=False) -> str:
        api_url = f"{self.base_url}/api/chat"
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "num_predict": max_tokens if max_tokens > 0 else -1, # -1 for until eos for some models
                "temperature": temperature
            }
        }
        try:
            print(f"INFO: Querying Ollama model: {model} at {self.base_url}...")
            response = requests.post(api_url, json=payload, timeout=300) # Longer timeout for local
            response.raise_for_status()
            
            full_response_content = ""
            if stream:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            full_response_content += data.get("message", {}).get("content", "")
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            print(f"WARNING: Ollama stream - could not decode JSON line: {line}")
            else:
                full_response_content = response.json().get("message", {}).get("content", "")
            
            print(f"INFO: Ollama response received.")
            return full_response_content
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Ollama API request failed: {e}. Is Ollama running at {self.base_url} and model '{model}' pulled/available?")
            return f"Error: Ollama request failed. {e}"
        except (KeyError, IndexError) as e:
            print(f"ERROR: Could not parse Ollama response: {e}")
            return "Error: Invalid response from Ollama."