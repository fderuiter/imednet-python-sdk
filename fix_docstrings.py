import os
import re

PLACEHOLDERS = [
    '"""TODO: Add docstring."""',
    '"""Documentation placeholder."""',
    "'''TODO: Add docstring.'''",
    "'''Documentation placeholder.'''",
]

def generate_docstring(lines, line_index, file_path):
    prev_line = ""
    for idx in range(line_index - 1, max(-1, line_index - 6), -1):
        line = lines[idx].strip()
        if line.startswith(("class ", "def ")):
            prev_line = line
            break

    is_test = "tests/" in file_path or "/test_" in file_path or os.path.basename(file_path).startswith("test_")

    match_class = re.search(r'class\s+([A-Za-z0-9_]+)', prev_line)
    if match_class:
        class_name = match_class.group(1)
        if is_test:
            return f'"""Test suite for {class_name}."""'
        return f'"""{class_name} implementation."""'

    match_def = re.search(r'def\s+([A-Za-z0-9_]+)', prev_line)
    if match_def:
        def_name = match_def.group(1)
        if is_test:
            return f'"""Test {def_name} behavior."""'
        if "providers-airflow" in file_path and "export.py" in file_path:
             format_name = def_name.replace("export_to_", "")
             return f'"""Export study records to {format_name} format."""'
        return f'"""Perform {def_name.replace("_", " ")} operation."""'

    is_module_doc = True
    for i in range(line_index):
        if lines[i].strip() and not lines[i].strip().startswith(("#", "from __future__")):
            is_module_doc = False
            break

    if is_module_doc:
        base_name = os.path.basename(file_path).replace(".py", "")
        if is_test:
            return f'"""Tests for {base_name}."""'
        return f'"""{base_name.replace("_", " ").title()} module."""'

    return '"""Implementation detail."""'

def fix_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    lines = content.splitlines(keepends=True)
    new_lines = []
    changed = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped in PLACEHOLDERS:
            indent = line[:line.find(stripped)]
            new_doc = generate_docstring(lines, i, file_path)
            new_lines.append(f"{indent}{new_doc}\n")
            changed = True
        else:
            new_lines.append(line)

    if changed:
        with open(file_path, 'w') as f:
            f.writelines(new_lines)
        return True
    return False

def main():
    count = 0
    dirs_to_scan = ["packages", "tests", "examples", "scripts"]
    for d in dirs_to_scan:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            if "site-packages" in root or "__pycache__" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    if fix_file(path):
                        count += 1
    print(f"Fixed docstrings in {count} files.")

if __name__ == "__main__":
    main()
