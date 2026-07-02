"""TODO: Add docstring."""

import json
import sys


def main():
    """TODO: Add docstring."""
    import os
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

    all_packages = [d for d in os.listdir('packages') if os.path.isdir(os.path.join('packages', d))]
    
    # Build dynamic impact map based on dependencies in pyproject.toml
    impact_map = {pkg: [pkg] for pkg in all_packages}
    for pkg in all_packages:
        toml_path = os.path.join('packages', pkg, 'pyproject.toml')
        if os.path.exists(toml_path):
            with open(toml_path, 'r', encoding='utf-8') as f:
                content_str = f.read()
                # Extremely simple parsing to avoid missing tomllib in base python 3.10
                for other_pkg in all_packages:
                    if pkg != other_pkg:
                        # If pkg depends on other_pkg, changing other_pkg impacts pkg
                        # imednet packages are prefixed with 'imednet' but folders are different
                        # 'core' is 'imednet'
                        # 'plugins-workflows' is 'imednet-workflows'
                        pkg_name_map = {
                            'core': 'imednet',
                            'plugins-workflows': 'imednet-workflows',
                            'providers-airflow': 'apache-airflow-providers-imednet',
                            'plugins-streamlit': 'imednet-streamlit',
                            'plugins-sinks': 'imednet-plugins-sinks'
                        }
                        search_name = pkg_name_map.get(other_pkg, other_pkg)
                        if search_name in content_str:
                            impact_map[other_pkg].append(pkg)

    lines = sys.stdin.read().splitlines()
    changed_files = [line.strip() for line in lines if line.strip()]

    if not changed_files:
        print(json.dumps(all_packages))
        return

    impacted = set()
    for file in changed_files:
        if file.startswith('packages/'):
            parts = file.split('/')
            if len(parts) > 1 and parts[1] in impact_map:
                impacted.update(impact_map[parts[1]])
            else:
                print(json.dumps(all_packages))
                return
        else:
            if file.startswith('docs/') or file.startswith('examples/') or file.endswith('.md'):
                continue
            print(json.dumps(all_packages))
            return

    if not impacted:
        impacted = ['core']

    print(json.dumps(list(impacted)))


if __name__ == "__main__":
    main()
