









4. Async client  
   • You bundle httpx already—consider adding an `AsyncClient` wrapper alongside your synchronous client so users can `await imednet.AsyncClient()`.




11. Strict typing  
   • You currently run mypy with `strict = false`. If possible, tighten certain modules (e.g. your models) to `strict = true` to guarantee full type coverage.

