"""TODO: Add docstring."""

import glob
import json
import os
import sys


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
            # simply split by >=, <=, ==, <, >
            for op in ['>=', '<=', '==', '<', '>', '[']:
                dep = dep.split(op)[0]
            parsed_deps.append(dep.strip())

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
        if not (file.startswith('docs/') or file.startswith('examples/') or file.endswith('.md')):
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
            if file.startswith('docs/') or file.startswith('examples/') or file.endswith('.md'):
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
