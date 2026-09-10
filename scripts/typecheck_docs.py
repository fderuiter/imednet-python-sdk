"""Script to extract and type-check Sphinx testcode blocks from documentation."""

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
        content = rst_file.read_text(encoding="utf-8")
        file_snippets = []
        lines = content.splitlines()
        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]
            if line.strip().startswith(".. testcode::"):
                i += 1
                # Skip initial empty/whitespace lines
                block_lines = []
                indent = None
                while i < n:
                    curr_line = lines[i]
                    if curr_line.strip() == "":
                        i += 1
                        continue
                    else:
                        indent = len(curr_line) - len(curr_line.lstrip())
                        break
                while i < n:
                    curr_line = lines[i]
                    if curr_line.strip() == "":
                        block_lines.append("")
                        i += 1
                        continue
                    curr_indent = len(curr_line) - len(curr_line.lstrip())
                    if indent is not None and curr_indent >= indent:
                        block_lines.append(curr_line[indent:])
                        i += 1
                    else:
                        break
                code_snippet = "\n".join(block_lines)
                if code_snippet.strip():
                    file_snippets.append(code_snippet)
                    count += 1
                continue
            i += 1

        if file_snippets:
            out_file = snippets_dir / f"{rst_file.stem}.py"
            out_file.write_text("\n\n".join(file_snippets), encoding="utf-8")

    print(f"Extracted {count} testcode snippets.")

    cmd = [
        sys.executable,
        "-m",
        "mypy",
        "--ignore-missing-imports",
        "--no-strict-optional",
        "--allow-untyped-decorators",
        str(snippets_dir),
    ]
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
