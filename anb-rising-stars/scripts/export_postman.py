#!/usr/bin/env python3
"""
Export Postman collection from OpenAPI schema.
Downloads the OpenAPI schema from running FastAPI server and converts it to Postman format.
"""

import json
import requests
import sys
from pathlib import Path
from typing import Any, Dict, List


def get_openapi_schema(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Fetch OpenAPI schema from running FastAPI server."""
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching OpenAPI schema: {e}")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        sys.exit(1)


def resolve_schema_ref(ref: str, components: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve $ref to actual schema."""
    if not ref.startswith("#/components/schemas/"):
        return {}

    schema_name = ref.split("/")[-1]
    return components.get("schemas", {}).get(schema_name, {})


def extract_example(schema: Dict[str, Any], components: Dict[str, Any]) -> Any:
    """Extract example from schema."""
    # If schema has example, use it
    if "example" in schema:
        return schema["example"]

    # If schema has $ref, resolve it
    if "$ref" in schema:
        resolved = resolve_schema_ref(schema["$ref"], components)
        return extract_example(resolved, components)

    # If schema has json_schema_extra with example
    if "json_schema_extra" in schema and "example" in schema["json_schema_extra"]:
        return schema["json_schema_extra"]["example"]

    return None


def build_postman_collection(openapi_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Convert OpenAPI schema to Postman collection."""
    components = openapi_schema.get("components", {})

    collection = {
        "info": {
            "name": openapi_schema["info"]["title"],
            "description": openapi_schema["info"]["description"],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [],
        "variable": [
            {"key": "base_url", "value": "http://localhost:8000", "type": "string"},
            {"key": "access_token", "value": "", "type": "string"},
            {"key": "video_id", "value": "", "type": "string"},
        ],
    }

    # Group by tags
    tags_dict: Dict[str, List[Dict[str, Any]]] = {}

    for path, path_item in openapi_schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.startswith("x-"):
                continue

            tags = operation.get("tags", ["Other"])
            tag = tags[0] if tags else "Other"

            if tag not in tags_dict:
                tags_dict[tag] = []

            # Build request
            request = {
                "method": method.upper(),
                "header": [],
                "url": {
                    "raw": f"{{{{base_url}}}}{path}",
                    "host": ["{{base_url}}"],
                    "path": path.strip("/").split("/") if path != "/" else [""],
                },
            }

            # Add Authorization header if needed
            if operation.get("security"):
                request["header"].append(
                    {"key": "Authorization", "value": "Bearer {{access_token}}"}
                )

            # Add request body
            if "requestBody" in operation:
                content = operation["requestBody"].get("content", {})

                if "application/json" in content:
                    schema_ref = content["application/json"].get("schema", {})
                    example = extract_example(schema_ref, components)

                    if example:
                        request["header"].append(
                            {"key": "Content-Type", "value": "application/json"}
                        )
                        request["body"] = {
                            "mode": "raw",
                            "raw": json.dumps(example, indent=2, ensure_ascii=False),
                        }

                elif "multipart/form-data" in content:
                    request["body"] = {
                        "mode": "formdata",
                        "formdata": [
                            {"key": "video_file", "type": "file", "src": ""},
                            {
                                "key": "title",
                                "value": "Mi mejor tiro de 3",
                                "type": "text",
                            },
                        ],
                    }

            # Add query parameters
            query_params = []
            for param in operation.get("parameters", []):
                if param.get("in") == "query":
                    query_params.append(
                        {
                            "key": param["name"],
                            "value": param.get("example", ""),
                            "disabled": False,
                        }
                    )

            if query_params:
                request["url"]["query"] = query_params

            item = {"name": operation.get("summary", path), "request": request}

            tags_dict[tag].append(item)

    # Build collection items
    for tag in sorted(tags_dict.keys()):
        collection["item"].append({"name": tag, "item": tags_dict[tag]})

    return collection


def main():
    """Main function."""
    print("Fetching OpenAPI schema from http://localhost:8000...")
    openapi_schema = get_openapi_schema()

    print("Converting to Postman collection...")
    collection = build_postman_collection(openapi_schema)

    output_path = (
        Path(__file__).parent.parent
        / "collections"
        / "ANB_Rising_Stars.postman_collection.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)

    print(f"Postman collection exported: {output_path}")
    print(
        f"   Total endpoints: {sum(len(item['item']) for item in collection['item'])}"
    )


if __name__ == "__main__":
    main()
