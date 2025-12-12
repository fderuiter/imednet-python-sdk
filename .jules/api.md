# Mednet API Documentation

## Endpoints
- Overview: https://portal.prod.imednetapi.com/docs
- Codings: https://portal.prod.imednetapi.com/docs/codings
- Error: https://portal.prod.imednetapi.com/docs/error
- Forms: https://portal.prod.imednetapi.com/docs/forms
- Header: https://portal.prod.imednetapi.com/docs/header
- Intervals: https://portal.prod.imednetapi.com/docs/intervals
- Jobs: https://portal.prod.imednetapi.com/docs/jobs
- Queries: https://portal.prod.imednetapi.com/docs/queries
- Record Revisions: https://portal.prod.imednetapi.com/docs/record-revisions
- Records: https://portal.prod.imednetapi.com/docs/records
- Sites: https://portal.prod.imednetapi.com/docs/sites
- Studies: https://portal.prod.imednetapi.com/docs/studies
- Subjects: https://portal.prod.imednetapi.com/docs/subjects
- Users: https://portal.prod.imednetapi.com/docs/users
- Variables: https://portal.prod.imednetapi.com/docs/variables
- Visits: https://portal.prod.imednetapi.com/docs/visits

## Filtering Syntax
- **Operators**: `<`, `<=`, `>`, `>=`, `==`, `!=`, `=~` (contains/regex).
- **Connectors**: `;` (AND), `,` (OR).
- **Constraint**: White space is not allowed between key, operator, and value.
- **Dates**: Must use UTC format (`YYYY-MM-DDTHH:MM:SSZ`) for `dateCreated`, `dateModified`.
- **recordDataFilter**: Special parameter for filtering questionnaire data. Supports `;` or `,` but not both simultaneously.
