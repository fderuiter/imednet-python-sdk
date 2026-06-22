import sys

from imednet.endpoints.registry import ENDPOINT_REGISTRY


def main():
    with open("/app/docs/rest_api_reference.rst", "w") as f:
        f.write("REST API Reference\n")
        f.write("==================\n\n")
        f.write(".. contents::\n")
        f.write("   :local:\n")
        f.write("   :depth: 1\n\n")

        for name, endpoint_cls in sorted(ENDPOINT_REGISTRY.items()):
            if not hasattr(endpoint_cls, 'PATH'):
                continue

            title = name.replace("_", " ").title()
            f.write(f"{title}\n")
            f.write("-" * len(title) + "\n\n")

            f.write(f"**Endpoint:** ``GET /{endpoint_cls.PATH.strip('/')}``\n\n")

            model = getattr(endpoint_cls, 'MODEL', None)
            if model:
                f.write("**Response Model:**\n\n")
                fields = model.model_fields
                for field_name, field in fields.items():
                    alias = field.alias or field_name
                    # try to get type name safely
                    try:
                        typ = str(field.annotation).replace("typing.", "")
                    except:
                        typ = "Any"
                    f.write(f"- ``{alias}`` ({typ})\n")
                f.write("\n")

    print("Generated API docs at /app/docs/rest_api_reference.rst")


if __name__ == "__main__":
    main()
