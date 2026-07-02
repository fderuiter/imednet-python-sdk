"""Script to extract and type-check Sphinx testcode blocks from documentation."""

import re
import subprocess
import sys
from pathlib import Path


def main():
    """Extract snippets from documentation and run mypy on them."""
    docs_dir = Path("docs")
    snippets_dir = Path("docs/_build/snippets")
    snippets_dir.mkdir(parents=True, exist_ok=True)

    for f in snippets_dir.glob("*.py"):
        f.unlink()

    count = 0
    for rst_file in docs_dir.rglob("*.rst"):
        if "_build" in rst_file.parts:
            continue
        content = rst_file.read_text()
        pattern = re.compile(r"\.\.\s+testcode::\s*\n((?:\s*\n)*(?:[ ]+.*\n?)*)")

        file_snippets = []
        for match in pattern.finditer(content):
            block = match.group(1)
            lines = block.splitlines()
            if not lines:
                continue

            indent = None
            for line in lines:
                if line.strip():
                    indent = len(line) - len(line.lstrip())
                    break
            if indent is None:
                continue

            stripped = [line[indent:] if len(line) >= indent else line for line in lines]
            file_snippets.append("\n".join(stripped))
            count += 1

        if file_snippets:
            out_file = snippets_dir / f"{rst_file.stem}.py"
            out_file.write_text("\n\n".join(file_snippets))

    print(f"Extracted {count} testcode snippets.")

    cmd = ["mypy", "--ignore-missing-imports", "--no-strict-optional", str(snippets_dir)]
    print("Running typecheck:", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr, file=sys.stderr)

    if res.returncode != 0:
        print("Documentation type-check failed.")
        sys.exit(1)
    print("Documentation type-check passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
