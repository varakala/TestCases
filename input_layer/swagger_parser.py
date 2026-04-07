import requests
import yaml
import json


def fetch_swagger_spec(url):
    """Fetch and parse a Swagger/OpenAPI spec from a URL."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
   # data = response.json()
    #print(data)
    content_type = response.headers.get("Content-Type", "")
    text = response.text

    if "yaml" in content_type or url.endswith((".yaml", ".yml")):
        spec = yaml.safe_load(text)
    else:
        try:
            spec = json.loads(text)
        except json.JSONDecodeError:
            spec = yaml.safe_load(text)

    return spec


def extract_endpoints(spec):
    """Extract all endpoints with their details from an OpenAPI spec."""
    endpoints = []
    base_path = spec.get("basePath", "")
    print("base path================"+base_path)
    paths = spec.get("paths", {})
    print("path ====================")
    print(paths)

    # Collect shared schemas for context
    definitions = spec.get("definitions", {}) or spec.get("components", {}).get("schemas", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ("get", "post", "put", "delete", "patch", "head", "options"):
                endpoint = {
                    "path": base_path + path,
                    "method": method.upper(),
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "parameters": _extract_parameters(details, spec),
                    "request_body": _extract_request_body(details, spec),
                    "responses": _extract_responses(details),
                    "tags": details.get("tags", []),
                }
                print("ENDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
                print(endpoint)
                endpoints.append(endpoint)

    return endpoints


def _resolve_ref(ref, spec):
    """Resolve a $ref pointer in the spec."""
    if not ref or not ref.startswith("#/"):
        return {}
    parts = ref.lstrip("#/").split("/")
    node = spec
    for part in parts:
        node = node.get(part, {})
    return node


def _extract_schema(schema, spec, depth=0):
    """Extract a readable schema representation, resolving $ref."""
    if depth > 5:
        return schema

    if "$ref" in schema:
        resolved = _resolve_ref(schema["$ref"], spec)
        return _extract_schema(resolved, spec, depth + 1)

    if schema.get("type") == "array" and "items" in schema:
        return {"type": "array", "items": _extract_schema(schema["items"], spec, depth + 1)}

    if schema.get("type") == "object" or "properties" in schema:
        props = {}
        for name, prop in schema.get("properties", {}).items():
            props[name] = _extract_schema(prop, spec, depth + 1)
        result = {"type": "object", "properties": props}
        if "required" in schema:
            result["required"] = schema["required"]
        return result

    return schema


def _extract_parameters(details, spec):
    """Extract parameter info from endpoint details."""
    params = []
    for param in details.get("parameters", []):
        if "$ref" in param:
            param = _resolve_ref(param["$ref"], spec)
        p = {
            "name": param.get("name", ""),
            "in": param.get("in", ""),
            "required": param.get("required", False),
            "type": param.get("type", param.get("schema", {}).get("type", "")),
            "description": param.get("description", ""),
        }
        if "schema" in param:
            p["schema"] = _extract_schema(param["schema"], spec)
        params.append(p)
    return params


def _extract_request_body(details, spec):
    """Extract request body info (OpenAPI 3.x)."""
    rb = details.get("requestBody", {})
    if not rb:
        return None
    content = rb.get("content", {})
    for media_type, media_obj in content.items():
        if "schema" in media_obj:
            return {
                "content_type": media_type,
                "required": rb.get("required", False),
                "schema": _extract_schema(media_obj["schema"], spec),
            }
    return None


def _extract_responses(details):
    """Extract response status codes and descriptions."""
    responses = {}
    for code, resp in details.get("responses", {}).items():
        responses[str(code)] = resp.get("description", "")
    return responses
