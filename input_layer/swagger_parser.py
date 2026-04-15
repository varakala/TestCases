import logging
import json
import yaml
import requests

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Swagger Fetching & Parsing
# -------------------------------------------------------------------
def fetch_swagger_spec(url):
    """Fetch and parse a Swagger/OpenAPI spec from a URL."""
    logger.info("Fetching Swagger spec | url=%s", url)

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        logger.debug(
            "Swagger spec fetched successfully | status=%d | bytes=%d",
            response.status_code,
            len(response.content),
        )
    except Exception:
        logger.exception("Failed to fetch Swagger spec | url=%s", url)
        raise

    content_type = response.headers.get("Content-Type", "")
    text = response.text
    logger.debug("Swagger content type | %s", content_type)

    try:
        if "yaml" in content_type or url.endswith((".yaml", ".yml")):
            spec = yaml.safe_load(text)
            logger.info("Swagger spec parsed as YAML")
        else:
            spec = json.loads(text)
            logger.info("Swagger spec parsed as JSON")
    except Exception:
        logger.exception("Failed to parse Swagger spec")
        raise

    return spec


# -------------------------------------------------------------------
# Endpoint Extraction
# -------------------------------------------------------------------
def extract_endpoints(spec):
    """Extract all endpoints with their details from an OpenAPI spec."""
    logger.info("Extracting endpoints from Swagger spec")

    endpoints = []
    base_path = spec.get("basePath", "")
    paths = spec.get("paths", {}) or {}

    logger.debug(
        "Swagger paths discovered | count=%d | base_path=%s",
        len(paths),
        base_path,
    )

    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() in {"get", "post", "put", "delete", "patch", "head", "options"}:
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
                endpoints.append(endpoint)

                logger.debug(
                    "Endpoint extracted | %s %s",
                    endpoint["method"],
                    endpoint["path"],
                )

    logger.info("Endpoint extraction complete | total=%d", len(endpoints))
    return endpoints


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def _resolve_ref(ref, spec):
    """Resolve a $ref pointer in the spec."""
    if not ref or not ref.startswith("#/"):
        logger.debug("Invalid or empty $ref encountered | ref=%s", ref)
        return {}

    parts = ref.lstrip("#/").split("/")
    node = spec
    for part in parts:
        node = node.get(part, {})

    logger.debug("Resolved $ref | ref=%s", ref)
    return node


def _extract_schema(schema, spec, depth=0):
    """Extract a readable schema representation, resolving $ref."""
    if depth > 5:
        logger.warning("Max schema recursion depth reached")
        return schema

    if "$ref" in schema:
        logger.debug("Resolving schema $ref | ref=%s", schema["$ref"])
        resolved = _resolve_ref(schema["$ref"], spec)
        return _extract_schema(resolved, spec, depth + 1)

    if schema.get("type") == "array" and "items" in schema:
        return {
            "type": "array",
            "items": _extract_schema(schema["items"], spec, depth + 1),
        }

    if schema.get("type") == "object" or "properties" in schema:
        props = {
            name: _extract_schema(prop, spec, depth + 1)
            for name, prop in schema.get("properties", {}).items()
        }
        result = {"type": "object", "properties": props}
        if "required" in schema:
            result["required"] = schema["required"]
        return result

    return schema


def _extract_parameters(details, spec):
    """Extract parameter info from endpoint details."""
    parameters = []

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

        parameters.append(p)

    logger.debug("Parameters extracted | count=%d", len(parameters))
    return parameters


def _extract_request_body(details, spec):
    """Extract request body info (OpenAPI 3.x)."""
    rb = details.get("requestBody")
    if not rb:
        return None

    for media_type, media_obj in rb.get("content", {}).items():
        if "schema" in media_obj:
            logger.debug("Request body schema found | content_type=%s", media_type)
            return {
                "content_type": media_type,
                "required": rb.get("required", False),
                "schema": _extract_schema(media_obj["schema"], spec),
            }
    return None


def _extract_responses(details):
    """Extract response status codes and descriptions."""
    responses = {
        str(code): resp.get("description", "")
        for code, resp in details.get("responses", {}).items()
    }

    logger.debug("Responses extracted | status_codes=%s", list(responses.keys()))
    return responses
