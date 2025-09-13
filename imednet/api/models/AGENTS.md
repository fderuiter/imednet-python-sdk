# AGENTS.md — imednet/models/

## Purpose
Typed request/response models.

## Rules
- Pydantic models with field docs.
- Stable deserialization. Backward compatible on optional fields.
- Serialization mirrors API spec. No business logic here.

## Tests
- Round-trip, unknown fields, nullability, enum coverage.
