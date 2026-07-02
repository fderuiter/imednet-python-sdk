"""TODO: Add docstring."""

import json
import sys
import os
import glob

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
        opt_deps = data.get('project', {}).get('optional-dependencies', {})
        all_deps = list(deps)
        for v in opt_deps.values():
            all_deps.extend(v)
            
        # extract package name from dependency strings (e.g. "imednet-workflows>=0.6.0" -> "imednet-workflows")
        parsed_deps = []
        for dep in all_deps:
            # simply split by >=, <=, ==, <, >
            for op in ['>=', '<=', '==', '<', '>', '[']:
                dep = dep.split(op)[0]
            parsed_deps.append(dep.strip())
            
        packages[pkg_dir] = {
            'name': pkg_name,
            'deps': parsed_deps
        }

    # map package name back to directory
    name_to_dir = {info['name']: dir_name for dir_name, info in packages.items() if info['name']}

    lines = sys.stdin.read().splitlines()
    changed_files = [line.strip() for line in lines if line.strip()]

    if not changed_files:
        print(json.dumps(list(packages.keys())))
        return

    # Check if all changed files are docs/examples/md
    all_ignored = True
    for file in changed_files:
        if not (file.startswith('docs/') or file.startswith('examples/') or file.endswith('.md')):
            all_ignored = False
            break
            
    if all_ignored:
        print(json.dumps([]))
        return
        
    impacted = set()
    for file in changed_files:
        if file.startswith('packages/'):
            parts = file.split('/')
            if len(parts) > 1 and parts[1] in packages:
                changed_pkg_dir = parts[1]
                impacted.add(changed_pkg_dir)
                changed_pkg_name = packages[changed_pkg_dir]['name']
                
                # find all packages that depend on changed_pkg_name
                # and transitive dependencies!
                # Wait, if A depends on B, and B changes, A is impacted.
                # If C depends on A, and B changes, C is impacted too.
                # So we need to compute reverse dependencies.
            else:
                # unknown package or something else in packages/
                print(json.dumps(list(packages.keys())))
                return
        else:
            if file.startswith('docs/') or file.startswith('examples/') or file.endswith('.md'):
                continue
            # some core file changed (like root Makefile, etc)
            print(json.dumps(list(packages.keys())))
            return
            
    # Compute transitive impacts
    added = True
    while added:
        added = False
        for pkg_dir, info in packages.items():
            if pkg_dir in impacted:
                continue
            # if this pkg depends on any of the impacted packages, it is also impacted
            for dep in info['deps']:
                dep_dir = name_to_dir.get(dep)
                if dep_dir and dep_dir in impacted:
                    impacted.add(pkg_dir)
                    added = True
                    break

    print(json.dumps(list(impacted)))

if __name__ == "__main__":
    main()
