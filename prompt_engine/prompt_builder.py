import json
import logging

logger = logging.getLogger(__name__)


def _build_prompt(endpoint):
    """Build a detailed prompt for test case generation."""
    logger.debug(
        "Building prompt | method=%s | path=%s",
        endpoint.get("method"),
        endpoint.get("path"),
    )

    # ------------------------------------------------------------------
    # Parameters section
    # ------------------------------------------------------------------
    params_text = ""
    parameters = endpoint.get("parameters", [])
    if parameters:
        logger.debug("Adding parameters to prompt | count=%d", len(parameters))
        params_text = "Parameters:\n"
        for p in parameters:
            params_text += (
                f"  - {p['name']} "
                f"(in: {p['in']}, type: {p['type']}, required: {p['required']}): "
                f"{p['description']}\n"
            )

    # ------------------------------------------------------------------
    # Request body section
    # ------------------------------------------------------------------
    body_text = ""
    request_body = endpoint.get("request_body")
    if request_body:
        logger.debug(
            "Adding request body to prompt | content_type=%s",
            request_body.get("content_type"),
        )
        body_text = f"Request Body ({request_body['content_type']}):\n"
        body_text += (
            f"  Schema: {json.dumps(request_body['schema'], indent=2)}\n"
        )

    # ------------------------------------------------------------------
    # Responses section
    # ------------------------------------------------------------------
    responses = endpoint.get("responses", {})
    logger.debug("Adding responses to prompt | count=%d", len(responses))

    responses_text = "Responses:\n"
    for code, desc in responses.items():
        responses_text += f"  {code}: {desc}\n"

    # ------------------------------------------------------------------
    # Final prompt assembly
    # ------------------------------------------------------------------
    prompt = f"""You are a QA engineer. Generate comprehensive test cases for the following REST API endpoint.

Endpoint: {endpoint['method']} {endpoint['path']}
Summary: {endpoint['summary']}
Description: {endpoint['description']}
Tags: {', '.join(endpoint['tags'])}
{params_text}
{body_text}
{responses_text}

Generate test cases covering:
1. Positive/happy path tests
2. Negative tests (invalid inputs, missing required fields)
3. Boundary value tests
4. Authentication/authorization tests (if applicable)
5. Edge cases

For EACH test case, respond in this exact JSON format (return a JSON array):
[
  {{
    "test_case_id": "TC_001",
    "test_scenario": "short scenario name",
    "test_description": "detailed description of what is being tested",
    "preconditions": "any setup needed",
    "test_steps": "step by step instructions",
    "test_data": "specific input data to use",
    "expected_result": "what should happen",
    "priority": "High/Medium/Low",
    "test_type": "Positive/Negative/Boundary/Security/Edge Case"
  }}
]

Return ONLY the JSON array, no other text.
"""

    logger.info(
        "Prompt built successfully | method=%s | path=%s | length=%d chars",
        endpoint.get("method"),
        endpoint.get("path"),
        len(prompt),
    )

    return prompt