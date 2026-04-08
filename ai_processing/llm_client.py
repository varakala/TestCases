import json
import requests
from prompt_engine.prompt_builder import _build_prompt
from validation_layer.validator import _parse_test_cases
OLLAMA_URL = "http://localhost:11434/api/chat"

#/api/generate
MODEL = "llama3.2"

def generate_test_cases(endpoint):
    """Generate test cases for a single API endpoint using Ollama Mistral."""
    prompt = _build_prompt(endpoint)
    response = _call_ollama(prompt)
    return _parse_test_cases(response, endpoint)
def _call_ollama(prompt):
    """Call Ollama API with the given prompt."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 4096,
        },
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=300)
    response.raise_for_status()
    return response.json().get("response", "")
