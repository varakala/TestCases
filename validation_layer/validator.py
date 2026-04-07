import json

def _parse_test_cases(response_text, endpoint):
    """Parse the LLM response into structured test cases."""
    # Try to extract JSON from the response
    text = response_text.strip()

    # Find JSON array in the response
    start = text.find("[")
    end = text.rfind("]")

    if start != -1 and end != -1:
        json_str = text[start : end + 1]
        try:
            cases = json.loads(json_str)
            # Enrich each case with endpoint info
            for case in cases:
                case["endpoint"] = f"{endpoint['method']} {endpoint['path']}"
                case["tags"] = ", ".join(endpoint["tags"])
            return cases
        except json.JSONDecodeError:
            pass

    # Fallback: return a single case indicating parsing failed
    return [
        {
            "test_case_id": "TC_001",
            "endpoint": f"{endpoint['method']} {endpoint['path']}",
            "tags": ", ".join(endpoint["tags"]),
            "test_scenario": "Manual review needed",
            "test_description": response_text[:500],
            "preconditions": "",
            "test_steps": "",
            "test_data": "",
            "expected_result": "",
            "priority": "Medium",
            "test_type": "Review",
        }
    ]
