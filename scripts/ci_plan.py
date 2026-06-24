"""TODO: Add docstring."""

import json
import sys


def main():
    """TODO: Add docstring."""
    all_packages = [
        'core',
        'plugins-workflows',
        'providers-airflow',
        'plugins-streamlit',
        'plugins-sinks',
    ]
    impact_map = {
        'core': [
            'core',
            'plugins-workflows',
            'providers-airflow',
            'plugins-streamlit',
            'plugins-sinks',
        ],
        'plugins-workflows': ['plugins-workflows', 'plugins-streamlit'],
        'providers-airflow': ['providers-airflow'],
        'plugins-streamlit': ['plugins-streamlit'],
        'plugins-sinks': ['plugins-sinks'],
    }

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
