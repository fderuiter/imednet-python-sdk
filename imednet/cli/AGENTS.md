# AGENTS.md — imednet/cli/

## Purpose
Stable CLI over the SDK.

## Rules
- Use Typer or argparse. Keep flags backward compatible.
- Pure I/O at edges. Business logic lives in `imednet/`.
- Exit codes: 0 success, non-zero on user or network errors.

## UX
- `--help` must be complete and correct.
- Log to stderr. Default level INFO. `--verbose/--quiet` supported.

## Tests
- Unit: parse args, map to SDK calls, error cases.
- Golden outputs for common commands.

## Docs
- Update CLI page and examples with every new flag/subcommand.
