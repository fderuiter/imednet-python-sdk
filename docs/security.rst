Security Controls & Policies
============================

The iMednet SDK implements a Universal Security Framework to guarantee that
Protected Health Information (PHI) and system credentials remain secure
across all data workflows and integrations.

Centralized Sensitivity Registry
--------------------------------

All redaction, masking, and sanitization logic is governed by a single,
centralized registry: :class:`~imednet.security.SensitivityRegistry`. This registry
replaces divergent security lists across different modules and UI components.

Keys are matched against exact lists (e.g. ``patient_name``, ``ssn``) and pattern
matchers (e.g. ``password``, ``token``, ``api_key``) to automatically identify
sensitive fields in unstructured data.

Redaction Middleware and Logging
--------------------------------

The system enforces automated redaction of sensitive data:

1. **API Requests & System Logs**: The :class:`~imednet.security.RedactionLogFilter`
   is automatically attached to the JSON logging configuration. It intercepts all
   outgoing log messages, automatically masking connection strings (e.g., stripping
   credentials from URIs) and redacting dictionary objects passed as log arguments
   if they match the sensitivity registry.

2. **Data Export & UI Displays**: Outbound data flows, such as CSV/Parquet exports
   and Streamlit data lineage views, automatically process the payload through
   the global registry, ensuring that any raw PHI is recursively replaced with
   the ``***MASKED***`` marker.

Validators (Injection and Traversal Protection)
-----------------------------------------------

The framework provides built-in validation functions to protect against common
attack vectors:

- :func:`~imednet.security.validate_header_value` prevents HTTP header injection
  by rejecting any value containing newline characters.
- :func:`~imednet.security.validate_partition_key` prevents directory traversal
  attacks by rejecting null bytes, absolute path modifiers, and relative path
  navigators (like ``../`` or ``..\\``).
- :func:`~imednet.security.sanitize_csv_formula` prevents CSV/Excel formula injection
  by sanitizing strings that begin with formula indicators (``=``, ``+``, ``-``, ``@``).
