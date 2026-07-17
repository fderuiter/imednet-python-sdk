import argparse
import ast
import os

PLACEHOLDER = '"""TODO: Add docstring."""'

def get_meaningful_docstring(node, filepath):
    if isinstance(node, ast.Module):
        if os.path.basename(filepath) == '__init__.py':
            return '"""Test package initialization."""'
        name = os.path.basename(filepath).replace('.py', '').replace('test_', '').replace('_', ' ')
        return f'"""Unit tests for {name}."""'

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == '__init__':
            return '"""Initialize the test object."""'
        if node.name.startswith('test_'):
            name = node.name[5:].replace('_', ' ')
            suffix = " asynchronously" if isinstance(node, ast.AsyncFunctionDef) else ""
            return f'"""Test that {name}{suffix}."""'
        name = node.name.replace('_', ' ')
        return f'"""Helper function to {name}."""'

    if isinstance(node, ast.ClassDef):
        name = node.name.replace('Test', '').replace('_', ' ')
        return f'"""Test suite for {name}."""'

    return PLACEHOLDER

def process_file(filepath):
    with open(filepath) as f:
        content = f.read()

    if PLACEHOLDER not in content:
        return

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return

    modifications = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node, clean=False)
            if docstring == "TODO: Add docstring.":
                for body_node in node.body:
                    if isinstance(body_node, ast.Expr) and isinstance(
                        body_node.value, (ast.Constant, ast.Str)
                    ):
                        val = (
                            body_node.value.value
                            if isinstance(body_node.value, ast.Constant)
                            else body_node.value.s
                        )
                        if val == "TODO: Add docstring.":
                            new_doc = get_meaningful_docstring(node, filepath)
                            modifications.append((body_node.lineno, new_doc))
                            break

    lines = content.splitlines()
    for lineno, new_doc in sorted(modifications, reverse=True):
        idx = lineno - 1
        if idx < len(lines) and PLACEHOLDER in lines[idx]:
            lines[idx] = lines[idx].replace(PLACEHOLDER, new_doc)
        else:
            for i in range(max(0, idx - 5), min(len(lines), idx + 6)):
                if PLACEHOLDER in lines[i]:
                    lines[i] = lines[i].replace(PLACEHOLDER, new_doc)
                    break

    new_content = '\n'.join(lines)
    if not new_content.endswith('\n') and content.endswith('\n'):
        new_content += '\n'

    with open(filepath, 'w') as f:
        f.write(new_content)

def main():
    parser = argparse.ArgumentParser(description="Generate and patch missing docstrings using AST.")
    parser.add_argument("targets", nargs="*", default=["tests"], help="Target directories or files to patch (defaults to 'tests').")
    args = parser.parse_args()
    
    for target in args.targets:
        if os.path.isfile(target):
            if target.endswith(".py"):
                process_file(target)
        elif os.path.isdir(target):
            for root, _, files in os.walk(target):
                for file in files:
                    if file.endswith('.py'):
                        process_file(os.path.join(root, file))
        else:
            print(f"Warning: Target '{target}' not found or is invalid.")

if __name__ == '__main__':
    main()
