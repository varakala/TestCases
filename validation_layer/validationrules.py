def generate_validation_test_cases(endpoint):
    """
    Generate validation test cases for mandatory, min/max, empty fields.
    """
    test_cases = []

    request_body = endpoint.get("request_body")
    if not request_body:
        return test_cases

    schema = request_body.get("schema", {})
    rules = extract_validation_rules(schema)

    for rule in rules:
        field = rule["field"]

        # ✅ Missing mandatory field
        if rule["required"]:
            test_cases.append({
                "test_scenario": f"Missing mandatory field: {field}",
                "test_description": f"Verify API returns error when mandatory field '{field}' is missing",
                "preconditions": "Valid authentication",
                "test_steps": f"Send request without '{field}'",
                "test_data": f"{{'{field}': NOT PROVIDED}}",
                "expected_result": f"API should reject request with validation error for missing '{field}'",
                "priority": "High",
                "test_type": "Negative",
            })

        # ✅ Empty field
        test_cases.append({
            "test_scenario": f"Empty value for field: {field}",
            "test_description": f"Verify API behavior when '{field}' is empty",
            "preconditions": "Valid authentication",
            "test_steps": f"Send request with '{field}' as empty value",
            "test_data": f"{{'{field}': ''}}",
            "expected_result": "API should return validation error",
            "priority": "Medium",
            "test_type": "Negative",
        })

        # ✅ Min validation
        if rule["min"] is not None:
            test_cases.append({
                "test_scenario": f"Min constraint validation for {field}",
                "test_description": f"Verify API rejects '{field}' below minimum value",
                "preconditions": "Valid authentication",
                "test_steps": f"Send request with '{field}' < {rule['min']}",
                "test_data": f"{{'{field}': {rule['min'] - 1}}}",
                "expected_result": "API should return validation error",
                "priority": "High",
                "test_type": "Boundary",
            })

        # ✅ Max validation
        if rule["max"] is not None:
            test_cases.append({
                "test_scenario": f"Max constraint validation for {field}",
                "test_description": f"Verify API rejects '{field}' above maximum value",
                "preconditions": "Valid authentication",
                "test_steps": f"Send request with '{field}' > {rule['max']}",
                "test_data": f"{{'{field}': {rule['max'] + 1}}}",
                "expected_result": "API should return validation error",
                "priority": "High",
                "test_type": "Boundary",
            })

    return test_cases
def extract_validation_rules(schema, parent_required=None):
    """
    Extract validation rules (required, min, max, empty) from a schema.
    """
    rules = []

    if not schema:
        return rules

    if schema.get("type") != "object":
        return rules

    properties = schema.get("properties", {})
    required_fields = schema.get("required", parent_required or [])

    for field, details in properties.items():
        field_rules = {
            "field": field,
            "required": field in required_fields,
            "type": details.get("type"),
            "min": details.get("minimum") or details.get("minLength"),
            "max": details.get("maximum") or details.get("maxLength"),
            "nullable": details.get("nullable", False),
        }
        rules.append(field_rules)

        # Nested object handling
        if details.get("type") == "object":
            rules.extend(
                extract_validation_rules(
                    details, parent_required=details.get("required", [])
                )
            )

    return rules