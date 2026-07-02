import subprocess
import shutil
from pathlib import Path
import os
import sys

def run_command(cmd, env=None, check=True):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, env=env, check=check)

def main():
    api_dir = Path("docs/api")
    
    print("Cleaning old API docs...")
    if api_dir.exists():
        shutil.rmtree(api_dir)
        
    print("Generating new API docs...")
    env = os.environ.copy()
    env["SPHINX_APIDOC_OPTIONS"] = "members,show-inheritance"
    
    # Core package
    run_command([
        "sphinx-apidoc", "-o", str(api_dir),
        "packages/core/src/imednet",
        "packages/core/src/imednet/core",
        "packages/core/src/imednet/compat",
        "packages/core/src/imednet/http",
        "-f", "-M", "--tocfile", "core"
    ], env=env)
    
    # Other packages
    packages_dir = Path("packages")
    for pkg in packages_dir.iterdir():
        if pkg.is_dir() and pkg.name != "core":
            src_dir = pkg / "src"
            if src_dir.exists():
                subdirs = [d for d in src_dir.iterdir() if d.is_dir()]
                if subdirs:
                    target_dir = subdirs[0]
                    run_command([
                        "sphinx-apidoc", "-o", str(api_dir),
                        str(target_dir),
                        "-f", "-M", "--tocfile", pkg.name
                    ], env=env)
                    
    print("Validating mermaid diagrams...")
    run_command([sys.executable, "scripts/validate_diagrams.py"])
    
    print("Validating documentation...")
    run_command([sys.executable, "scripts/validate_docs.py"])
    
    print("Building HTML...")
    run_command([
        "sphinx-build", "-b", "html", "-W", "--keep-going",
        "docs", "docs/_build/html"
    ])

if __name__ == "__main__":
    main()
