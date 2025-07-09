# AGENTS.md – Documentation Rules (Sphinx)

## Purpose  
Ensure the Sphinx site builds consistently and remains readable for both humans and Codex-style agents.

---

## Build & preview

```bash
# generate HTML docs locally
make docs      # alias for `sphinx-build -b html docs/ build/docs`

# open the result
open build/docs/index.html  # or `python -m webbrowser`
````

* CI calls the same `make docs` target; the build **MUST** succeed without warnings.

---

## reStructuredText conventions

| Guideline                                                                    | Example                                                              |
| ---------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Wrap code longer than ≈ 15 lines in a collapsible block.                     | `rst  .. collapse:: Usage example      `python      >>> ...   \`\`\` |
| Prefer **NumPy-style** docstrings in source files; autodoc will render them. | —                                                                    |
| Use `:class:`, `:func:` & `:py:meth:` roles for cross-referencing.           | —                                                                    |
| Keep headings sequential (`===`, `---`, `^^^`).                              | —                                                                    |

**DO NOT** embed raw HTML; stick to RST directives so themes remain portable.

---

## Structure & navigation

* Top-level toctree lives in `docs/index.rst`; **MUST** list every new page.
* Tutorials belong in `docs/tutorials/`; API reference is auto-generated from `imednet/`.
* If you add third-party libraries that need mocking, declare them in `docs/conf.py` → `autodoc_mock_imports`.

---

## Style checks

* Run `poetry run doc8 docs/` before committing to catch line-length or indentation issues.
* Spell-check with `codespell`; add accepted domain terms to `docs/.codespell-ignore`.

---

## Publishing

The GitHub Pages site is rebuilt by the **release workflow** after every version tag (`v*`).
Failing to keep the docs build-clean will block the PyPI publish step.

````
