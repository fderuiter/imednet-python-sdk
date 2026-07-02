Verification Reports
====================

The automated CI pipeline relies on a structured JSON schema for reporting verification results, eliminating brittle log-parsing logic.

Unified Verification Model
--------------------------

All testing suites (e.g., fuzzing, performance, live drift detection) must output a structured JSON file matching the ``VerificationReport`` model defined in ``imednet.models.verification``.

The central model requires:
- ``version``: The schema version (e.g., ``"1.0"``).
- ``track``: The verification track (e.g., ``"fuzzing"``, ``"performance"``, ``"validation"``, ``"live_tests"``, ``"drift"``).
- ``status``: Pass or fail outcome.
- ``violations``: A list of specific errors or rule violations (using ``VerificationViolation``).
- ``metrics``: An optional list of performance metrics (using ``VerificationPerformanceMetric``).
- ``summary``: A human-readable summary.

Extending the Report Schema
---------------------------

If you need to add a new verification type, extend the ``Literal`` for the ``track`` field in ``VerificationReport`` inside ``packages/core/src/imednet/models/verification.py``. 

To add new fields or structures specific to your testing, use the standard Pydantic inheritance patterns or add optional fields to the existing models.

Writing Reports in CI
---------------------

Your testing suite should generate a JSON file matching ``*_report.json`` in the workspace directory (e.g., ``fuzzing_report.json``).

The CI pipeline uses ``scripts/aggregate_verification.py`` to aggregate all ``*_report.json`` files, validate them against the schema, and automatically construct human-readable PR comments or fail the job if a report is malformed or violations are found.
