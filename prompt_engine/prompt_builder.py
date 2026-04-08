import json
def _build_prompt(endpoint):
    """Build a detailed prompt for test case generation."""
    params_text = ""
    if endpoint["parameters"]:
        params_text = "Parameters:\n"
        for p in endpoint["parameters"]:
            params_text += f"  - {p['name']} (in: {p['in']}, type: {p['type']}, required: {p['required']}): {p['description']}\n"

    body_text = ""
    if endpoint["request_body"]:
        body_text = f"Request Body ({endpoint['request_body']['content_type']}):\n"
        body_text += f"  Schema: {json.dumps(endpoint['request_body']['schema'], indent=2)}\n"

    responses_text = "Responses:\n"
    for code, desc in endpoint["responses"].items():
        responses_text += f"  {code}: {desc}\n"

    return f"""Act as senior API test engineer, Generate comprehensive API test matrices from OpenAPI operation fragments. Emit ONLY strict JSON that conforms to the given schema.

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
