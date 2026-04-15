import json
import logging
import requests

from prompt_engine.prompt_builder import _build_prompt
from validation_layer.validator import _parse_test_cases

# -------------------------------------------------------------------
# Logger setup
# -------------------------------------------------------------------
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------
def generate_test_cases(endpoint):
    """
    Generate test cases for a single API endpoint using Ollama (Mistral).
    """
    logger.info("Generating test cases | endpoint=%s", endpoint.get("path"))

    try:
        prompt = _build_prompt(endpoint)
        logger.debug("Prompt built successfully | length=%d chars", len(prompt))

        response = _call_ollama(prompt)
        logger.debug("Received LLM response | length=%d chars", len(response))

        test_cases = _parse_test_cases(response, endpoint)
        logger.info(
            "Test cases generated successfully | endpoint=%s | count=%d",
            endpoint.get("path"),
            len(test_cases) if test_cases else 0,
        )

        return test_cases

    except Exception:
        logger.exception(
            "Failed to generate test cases | endpoint=%s",
            endpoint.get("path"),
        )
        raise


# -------------------------------------------------------------------
# Internal helpers
# -------------------------------------------------------------------
def _call_ollama(prompt):
    """
    Call Ollama API with the given prompt.
    """
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 4096,
        },
    }

    logger.info("Calling Ollama API | model=%s", MODEL)
    logger.debug("Ollama payload prepared")

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=300,
        )
        response.raise_for_status()

        logger.debug(
            "Ollama response received | status=%s | headers=%s",
            response.status_code,
            response.headers.get("Content-Type"),
        )

        result = response.json().get("response", "")
        logger.info("Ollama call successful | response_length=%d", len(result))
        return result

    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out | url=%s", OLLAMA_URL)
        raise

    except requests.exceptions.RequestException:
        logger.exception("HTTP error while calling Ollama | url=%s", OLLAMA_URL)
        raise

    except ValueError:
        logger.exception("Invalid JSON response from Ollama")
        raise