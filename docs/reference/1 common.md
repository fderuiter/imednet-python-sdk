# Mednet EDC REST API Overview

The **Mednet EDC (Electronic Data Capture) REST API** offers a unified access point for retrieving data stored within iMednet data services. This API allows Sponsors, CROs, and other validated clients to securely access data using HTTP **GET** requests, provided the necessary security credentials are validated.

This API empowers iMednet users to:

- Export data to third-party reporting tools
- Display data in custom applications, mobile apps, or websites
- Store data in data warehouses
- Compile custom audit trails

All API responses are returned in **JSON** format (`application/json`), offering flexibility and simplicity when manipulating data.

---

## Base URL

The base URL to access the API is:

```text
https://edc.prod.imednetapi.com
```

To call an endpoint, append the route to the base URL. For example:

```text
https://edc.prod.imednetapi.com/api/v1/edc/studies
```

---

## Security and Validation

- **API Keys** must remain confidential. Avoid sharing or exposing keys publicly to prevent unauthorized access.
- **CORS** can inadvertently expose keys and should be avoided.

To authenticate, include the following headers in each request:

```json
{
  "x-api-key": "your-imednet-supplied-api-key",
  "x-imn-security-key": "your-imednet-supplied-security-key"
}
```

### Example Request Using `curl`

```bash
curl -X GET https://edc.prod.imednetapi.com/api/v1/edc/studies/STUDYKEY/sites \
  -H 'x-api-key: XXXXXXXX' \
  -H 'x-imn-security-key: XXX-XXX-XX-XXXXXX' \
  -H 'Content-Type: application/json'
```

---

## HTTP Verbs

| Verb | Usage                  |
|------|------------------------|
| GET  | Retrieve a resource    |
| POST | Insert data            |

---

## Status Codes

| Code | Description                                                                                      |
|------|--------------------------------------------------------------------------------------------------|
| 200  | OK - Request completed successfully                                                              |
| 400  | Bad Request - Malformed request. Error details provided in response                              |
| 401  | Unauthorized - Security issue with authentication headers. Error details provided                |
| 403  | Forbidden - Likely due to invalid `studyKey`. Error details provided                             |
| 404  | Not Found - Resource could not be found. Error details provided                                  |
| 429  | Too Many Requests - Rate limit exceeded. Contact Mednet support                                  |
| 500  | Internal Server Error - Unknown server error. Contact Mednet support                             |

---

## Resources

### Filtering

The iMednet REST API supports filtering results using specific criteria. Filter attributes are **case-sensitive** and vary by endpoint.

#### Key Attributes

| Endpoint          | Key Attributes                                                                                 |
|-------------------|-----------------------------------------------------------------------------------------------|
| **Study**         | `studyKey`, `studyType`, `studyName`, `dateCreated`, `dateModified`                            |
| **Site**          | `siteId`, `siteName`, `siteEnrollmentStatus`, `dateCreated`, `dateModified`                   |
| **Form**          | `formId`, `formKey`, `formName`, `formType`, `dateCreated`, `dateModified`                    |
| **Visit**         | `intervalId`, `intervalName`, `intervalGroupId`, `intervalGroupName`, `dateCreated`, `dateModified` |
| **Record**        | `intervalId`, `formId`, `formKey`, `siteId`, `recordId`, `parentRecordId`, `recordType`, `recordStatus`, `subjectKey`, `dateCreated`, `dateModified` |
| **Record Revision** | `recordRevisionId`, `recordId`, `recordOid`, `recordRevision`, `dataRevision`, `recordStatus`, `user`, `reasonForChange`, `dateCreated` |
| **Variable**      | `variableId`, `variableType`, `variableName`, `dateCreated`, `dateModified`, `formId`, `formKey`, `formName`, `label` |
| **Coding**        | `siteId`, `subjectId`, `formId`, `recordId`, `revision`, `variable`, `value`, `code`, `codedBy`, `reason`, `dictionaryName`, `dictionaryVersion`, `dateCoded` |

---

### Filtering Operators

| Operator | Description        |
|----------|--------------------|
| `<`      | Less than          |
| `<=`     | Less than or equal |
| `>`      | Greater than       |
| `>=`     | Greater or equal   |
| `==`     | Equal              |
| `!=`     | Not equal          |

---

### Connectors

| Connector | Description   |
|-----------|---------------|
| `and` / `;` | AND condition |
| `or` / `,` | OR condition  |

---

### Date Handling

- **Dates** are returned in **UTC**.
- When filtering, use UTC format unless otherwise specified.

| Attribute                   | Description                                        |
|-----------------------------|----------------------------------------------------|
| `dateCreated`               | Entity creation timestamp                          |
| `dateModified`              | Last modified timestamp                            |
| `startDate` (Visits)        | Subject visit start date                           |
| `endDate` (Visits)          | Subject visit end date                             |
| `dueDate` (Visits)          | Subject visit due date                             |
| `visitDate` (Visits)        | Actual subject visit date                          |

#### Supported Date Formats

| Format                        | Example                  | Description                        |
|-------------------------------|--------------------------|------------------------------------|
| `YYYY-MM-DDTHH:MM:SSZ`        | `2024-01-01T12:00:00Z`   | UTC time                          |
| `YYYY-MM-DDTHH:MM:SS-06:00`   | `2024-01-01T12:00:00-06:00` | CST time                      |
| `YYYY-MM-DD`                  | `2024-01-01`            | Date only (specific to Visits)     |

---

## Filter Examples

| Filter Value                              | Expected Result                                              |
|-------------------------------------------|--------------------------------------------------------------|
| `formId > 10`                             | Forms with `formId` greater than 10                          |
| `formType == "SUBJECT"`                   | Forms where `formType` is "SUBJECT"                          |
| `formId > 10;formType == "SUBJECT"`       | Subject forms with `formId` > 10                             |
| `formId > 10,formType == "SUBJECT"`       | Forms with `formId` > 10 **OR** `formType` == "SUBJECT"      |
| `dateCreated>2000-11-05T14:00:00Z`        | Entities created after Nov 5, 2000, 14:00 UTC                |
| `visitDate<2019-03-19`                    | Entities with `visitDate` before March 19, 2019              |

---

## Filtering on Record Data

The `recordData` attribute is dynamic, based on the form design in iMednet. Use the **recordDataFilter** parameter to filter within `recordData`.

- **AND** connector: `;`
- **OR** connector: `,`
- **Note**: You cannot mix both connectors in a single filter.

### Supported Operators for `recordDataFilter`

| Operator | Description                  |
|----------|------------------------------|
| `<`      | Less than                    |
| `<=`     | Less than or equal           |
| `>`      | Greater than                 |
| `>=`     | Greater than or equal        |
| `==`     | Equal                        |
| `!=`     | Not equal                    |
| `=~`     | Contains (case-insensitive, supports regex) |

---

### RecordDataFilter Examples

| Filter Value                           | Expected Result                                          |
|----------------------------------------|----------------------------------------------------------|
| `AESER==Serious`                       | Serious adverse events                                   |
| `AESER==Serious;GENDER==Male`          | Serious adverse events for male subjects                 |
| `AESER==Bronchitis,AGE>65`             | Bronchitis cases or subjects older than 65               |
| `AESER==bronch`                        | Adverse events containing "bronch" (case-insensitive)    |
| `AESER==Bronchitis;GENDER==Male,AGE>=65` | **400 Bad Request** — Mixed connectors not allowed      |

---

## Pre-conditions for Valid Filters

| Criteria                                   | Example                              |
|--------------------------------------------|--------------------------------------|
| Use `;` to separate AND conditions         | `number>1;name==John`                |
| No spaces between key, operator, or value  | `number>1` (✅), `number > 1` (❌)    |
| Values must directly follow operators      | `name==John`                         |
| Avoid conflicting filters                  | `name==John;name!=John` (❌ Invalid) |
| Use correct date format                    | `dateCreated>2018-01-01T06:00:00Z`   |
| All filters are case-sensitive             | `name==John` vs `name==john`         |
