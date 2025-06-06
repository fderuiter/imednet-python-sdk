Coding Review Workflow
=====================

The :class:`~imednet.workflows.coding_review.CodingReviewWorkflow` provides
utilities to inspect codings within a study and highlight potential issues.

Functions include:

* ``list_codings`` - retrieve codings using optional filter criteria.
* ``get_uncoded_items`` - return items where no code has been assigned.
* ``get_inconsistent_codings`` - detect variable/value pairs coded with multiple
  different codes.

These helpers build upon the ``codings`` endpoint to simplify quality checks
for medical coding data.
