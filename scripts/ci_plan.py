"""TODO: Add docstring."""

import glob
import json
import os
import re
import sys


def parse_dependency_name(dep_str: str) -> str:
    """
    Extracts the base package name from a PEP 508 dependency string.
    This safely strips out optional extras, version bounds, and environment markers.
    """
    match = re.match(r'^([a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?)', dep_str.strip())
    if match:
        return match.group(1)
    return dep_str.strip()


def main():
    """TODO: Add docstring."""
    import tomllib

    packages = {}
    for pyproject in glob.glob('packages/*/pyproject.toml'):
        with open(pyproject, 'rb') as f:
            data = tomllib.load(f)
        pkg_dir = os.path.basename(os.path.dirname(pyproject))
        pkg_name = data.get('project', {}).get('name')

        deps = data.get('project', {}).get('dependencies', [])
        # Dropping optional cycle linkages
        all_deps = list(deps)

        # extract package name from dependency strings (e.g. "imednet-workflows>=0.6.0" -> "imednet-workflows")
        parsed_deps = []
        for dep in all_deps:
            parsed_deps.append(parse_dependency_name(dep))

        packages[pkg_dir] = {'name': pkg_name, 'deps': parsed_deps}

    # map package name back to directory
    name_to_dir = {info['name']: dir_name for dir_name, info in packages.items() if info['name']}

    lines = sys.stdin.read().splitlines()
    changed_files = [line.strip() for line in lines if line.strip()]

    def fallback():
        print(json.dumps({"test": list(packages.keys()), "build": list(packages.keys())}))
        sys.exit(0)

    if not changed_files:
        fallback()

    # Check if all changed files are docs/examples/md
    all_ignored = True
    for file in changed_files:
        if not (file.startswith(('docs/', 'examples/')) or file.endswith('.md')):
            all_ignored = False
            break

    if all_ignored:
        print(json.dumps({"test": [], "build": []}))
        return

    build_impacted = set()
    test_only_impacted = set()

    for file in changed_files:
        if file.startswith('packages/'):
            parts = file.split('/')
            if len(parts) > 1 and parts[1] in packages:
                changed_pkg_dir = parts[1]
                if len(parts) > 2 and parts[2] == 'tests':
                    test_only_impacted.add(changed_pkg_dir)
                else:
                    build_impacted.add(changed_pkg_dir)
            else:
                # unknown package or something else in packages/
                fallback()
        else:
            if file.startswith(('docs/', 'examples/')) or file.endswith('.md'):
                continue
            # some core file changed (like root Makefile, etc)
            fallback()

    # Compute transitive impacts
    behavior_changed = set(build_impacted)
    added = True
    while added:
        added = False
        for pkg_dir, info in packages.items():
            if pkg_dir in behavior_changed:
                continue
            # if this pkg depends on any of the packages whose behavior changed, its behavior might change too
            for dep in info['deps']:
                dep_dir = name_to_dir.get(dep)
                if dep_dir and dep_dir in behavior_changed:
                    behavior_changed.add(pkg_dir)
                    added = True
                    break

    test_impacted = behavior_changed.union(test_only_impacted)
    print(json.dumps({"build": list(build_impacted), "test": list(test_impacted)}))


if __name__ == "__main__":
    main()
