## 2024-05-23 - .gitignore Wildcards Block Examples
**Insight:** The `.gitignore` file contained `.env.*`, which unintentionally ignored the `.env.example` file. This prevents example configurations from being committed unless explicitly un-ignored.
**Guideline:** When adding `.*` wildcards to `.gitignore`, always check if there are legitimate files (like documentation or examples) that match the pattern, and whitelist them using `!filename`.
