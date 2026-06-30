import ast
import os
import re

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
        else:
            name = node.name.replace('_', ' ')
            return f'"""Helper function to {name}."""'

    if isinstance(node, ast.ClassDef):
        name = node.name.replace('Test', '').replace('_', ' ')
        return f'"""Test suite for {name}."""'

    return PLACEHOLDER

def process_file(filepath):
    with open(filepath, 'r') as f:
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
            # Check for docstring
            docstring = ast.get_docstring(node, clean=False)
            if docstring == "TODO: Add docstring.":
                # Find the line number of the docstring.
                for body_node in node.body:
                    if isinstance(body_node, ast.Expr) and isinstance(body_node.value, (ast.Constant, ast.Str)):
                        val = body_node.value.value if isinstance(body_node.value, ast.Constant) else body_node.value.s
                        if val == "TODO: Add docstring.":
                            new_doc = get_meaningful_docstring(node, filepath)
                            modifications.append((body_node.lineno, new_doc))
                            break

    if not modifications:
        # Sometimes there's a TODO at the very top of the file that ast doesn't pick up if it's not a proper docstring?
        # No, ast.Module should pick it up.
        # But let's check for any remaining placeholders manually if needed.
        pass

    lines = content.splitlines()
    for lineno, new_doc in sorted(modifications, reverse=True):
        idx = lineno - 1
        if idx < len(lines) and PLACEHOLDER in lines[idx]:
            lines[idx] = lines[idx].replace(PLACEHOLDER, new_doc)
        else:
            found = False
            for i in range(max(0, idx-5), min(len(lines), idx+6)):
                if PLACEHOLDER in lines[i]:
                    lines[i] = lines[i].replace(PLACEHOLDER, new_doc)
                    found = True
                    break

    new_content = '\n'.join(lines)
    if not new_content.endswith('\n') and content.endswith('\n'):
        new_content += '\n'

    with open(filepath, 'w') as f:
        f.write(new_content)

def main():
    for root, dirs, files in os.walk('tests'):
        for file in files:
            if file.endswith('.py'):
                process_file(os.path.join(root, file))

if __name__ == '__main__':
    main()
