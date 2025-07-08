from pathlib import Path
import re


def get_mermaid_lines(path: Path):
    lines = []
    inside = False
    skip_blank = False
    with path.open() as f:
        for i, line in enumerate(f, 1):
            if line.strip() == ".. mermaid::":
                inside = True
                skip_blank = True
                continue
            if inside:
                if skip_blank and line.strip() == "":
                    continue
                skip_blank = False
                if line.strip() == "" or not line.startswith("   "):
                    inside = False
                    continue
                lines.append((i, line.lstrip()))
    return lines


PATTERN = re.compile(r"\[[^\]]*\([^\)]*\)\]")


def test_no_unquoted_parentheses_in_mermaid_blocks():
    errors = []
    for path in Path("docs").rglob("*.rst"):
        if "_build" in path.parts:
            continue
        for lineno, text in get_mermaid_lines(path):
            if PATTERN.search(text):
                errors.append(f"{path}:{lineno}: {text.rstrip()}")
    assert not errors, "Unquoted parentheses in mermaid labels:\n" + "\n".join(errors)
