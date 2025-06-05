#!/usr/bin/env python3
"""Update CHANGELOG.md with recent commit messages.

This utility collects commit summaries since the latest git tag and
adds them under the "Unreleased" section. It is a lightweight helper to
keep the changelog current.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path


def last_tag() -> str | None:
    """Return the most recent git tag or ``None`` if none exist."""
    try:
        return (
            subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], text=True)
            .strip()
        )
    except subprocess.CalledProcessError:
        return None


def collect_messages(since: str | None) -> list[str]:
    """Return commit summaries since ``since`` (exclusive)."""
    range_spec = f"{since}..HEAD" if since else "HEAD"
    log = subprocess.check_output(["git", "log", range_spec, "--pretty=%s"], text=True)
    return [f"- {line}" for line in log.strip().splitlines() if line]


def main() -> None:
    changelog = Path("CHANGELOG.md")
    text = changelog.read_text()
    match = re.search(r"## \[Unreleased\]\n", text)
    if not match:
        raise SystemExit("Unreleased section not found")
    insert_at = match.end()
    messages = collect_messages(last_tag())
    if not messages:
        return
    updated = text[:insert_at] + "\n".join(messages) + "\n" + text[insert_at:]
    changelog.write_text(updated)


if __name__ == "__main__":
    main()
