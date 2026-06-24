"""Script to synchronize README code snippets with examples."""

import re
import sys
from pathlib import Path


def sync_readme(readme_path: str = "README.md", dry_run: bool = False) -> bool:
    """Synchronize the README file with code snippets."""
    readme_file = Path(readme_path)
    if not readme_file.exists():
        print(f"Error: {readme_path} not found.")
        return False

    content = readme_file.read_text()

    # Regex to find snippet blocks
    # It looks for <!-- SNIPPET START: path/to/file --> ... <!-- SNIPPET END -->
    pattern = re.compile(
        r"(<!--\s*SNIPPET START:\s*(?P<filepath>[^\s]+)\s*-->\n)(.*?)(<!--\s*SNIPPET END\s*-->)",
        re.DOTALL,
    )

    changed = False
    new_content = content

    def replacer(match):
        nonlocal changed
        start_marker = match.group(1)
        filepath = match.group("filepath")
        end_marker = match.group(3)
        old_snippet = match.group(2)

        source_file = Path(filepath)
        if not source_file.exists():
            print(f"Warning: Source file {filepath} not found.")
            return match.group(0)

        file_content = source_file.read_text().strip()
        new_snippet = f"```python\n{file_content}\n```\n"

        if new_snippet != old_snippet:
            changed = True

        return f"{start_marker}{new_snippet}{end_marker}"

    new_content = pattern.sub(replacer, content)

    if changed:
        if dry_run:
            print("Readme sync would change the README.md file.")
            return True  # Indicates drift
        else:
            readme_file.write_text(new_content)
            print("Successfully synced README.md.")
    else:
        print("README.md is already up to date.")

    return changed


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    drift = sync_readme(dry_run=dry_run)
    if dry_run and drift:
        sys.exit(1)
    elif dry_run and not drift:
        sys.exit(0)
