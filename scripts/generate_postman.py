import json
import os
import sys

from imednet.endpoints.registry import ENDPOINT_REGISTRY


def main():
    collection = {
        "info": {
            "name": "iMedNet REST API",
            "description": "Auto-generated Postman collection from iMedNet SDK models.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [],
    }

    for name, endpoint_cls in ENDPOINT_REGISTRY.items():
        if not hasattr(endpoint_cls, 'PATH'):
            continue

        path = endpoint_cls.PATH.strip("/")
        path_segments = path.split("/")

        query_params = []
        if name not in ["studies", "jobs"]:
            query_params.append(
                {
                    "key": "studyKey",
                    "value": "{{study_key}}",
                    "description": "The study identifier.",
                }
            )

        item = {
            "name": name.replace("_", " ").title(),
            "request": {
                "method": "GET",
                "header": [
                    {"key": "Authorization", "value": "Bearer {{api_key}}:{{security_key}}"}
                ],
                "url": {
                    "raw": f"{{{{base_url}}}}/{path}",
                    "host": ["{{base_url}}"],
                    "path": path_segments,
                    "query": query_params,
                },
            },
        }
        collection["item"].append(item)

    with open("/app/imednet.postman_collection.json", "w") as f:
        json.dump(collection, f, indent=4)

    print("Generated Postman collection at /app/imednet.postman_collection.json")


if __name__ == "__main__":
    main()
