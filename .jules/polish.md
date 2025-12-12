## 2024-10-24 - Implicit Dependencies via Reflection
**Smell:** Use of `sys.modules[self.__class__.__module__]` to look up `Paginator` classes by name, forcing every endpoint file to import `Paginator` even if unused (`noqa: F401`).
**Remedy:** Refactored `ListGetEndpointMixin` to import and use `Paginator` and `AsyncPaginator` directly. This removed implicit coupling and deleted unused imports from 12 files.
