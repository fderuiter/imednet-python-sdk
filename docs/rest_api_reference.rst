REST API Reference
==================

.. contents::
   :local:
   :depth: 1

Codings
-------

**Endpoint:** ``GET /codings``

**Response Model:**

- ``studyKey`` (Optional[str])
- ``siteName`` (Optional[str])
- ``siteId`` (Optional[int])
- ``subjectId`` (Optional[int])
- ``subjectKey`` (Optional[str])
- ``formId`` (Optional[int])
- ``formName`` (Optional[str])
- ``formKey`` (Optional[str])
- ``recordId`` (Optional[int])
- ``variable`` (Optional[str])
- ``value`` (Optional[str])
- ``codingId`` (Optional[int])
- ``code`` (Optional[str])
- ``codedBy`` (Optional[str])
- ``dictionaryName`` (Optional[str])
- ``dictionaryVersion`` (Optional[str])
- ``dateCoded`` (Optional[str])

Forms
-----

**Endpoint:** ``GET /forms``

**Response Model:**

- ``studyKey`` (Optional[str])
- ``formId`` (Optional[int])
- ``formKey`` (Optional[str])
- ``formName`` (Optional[str])
- ``formType`` (Optional[str])
- ``revision`` (Optional[int])
- ``dateCreated`` (Optional[str])
- ``dateModified`` (Optional[str])
- ``disabled`` (bool | None)
- ``subjectRecordReport`` (bool | None)
- ``unscheduledVisit`` (bool | None)
- ``eproForm`` (Optional[bool])
- ``allowCopy`` (Optional[bool])

Intervals
---------

**Endpoint:** ``GET /intervals``

**Response Model:**

- ``studyKey`` (Optional[str])
- ``intervalId`` (Optional[int])
- ``intervalName`` (Optional[str])
- ``intervalDescription`` (Optional[str])
- ``intervalSequence`` (Optional[int])
- ``intervalGroupId`` (Optional[int])
- ``intervalGroupName`` (Optional[str])
- ``disabled`` (Optional[bool])
- ``dateCreated`` (Optional[str])
- ``dateModified`` (Optional[str])
- ``forms`` (list[imednet.models.intervals.FormSummary] | None)

Jobs
----

**Endpoint:** ``GET /jobs``

**Response Model:**

- ``jobId`` (Optional[str])
- ``batchId`` (Optional[str])
- ``state`` (Optional[str])
- ``dateCreated`` (Optional[str])
- ``dateStarted`` (Optional[str])
- ``dateFinished`` (Optional[str])
- ``progress`` (Optional[int])
- ``resultUrl`` (Optional[str])
- ``results`` (Any)

Queries
-------

**Endpoint:** ``GET /queries``

**Response Model:**

- ``studyKey`` (Optional[str])
- ``subjectId`` (Optional[int])
- ``annotationId`` (Optional[int])
- ``description`` (Optional[str])
- ``recordId`` (Optional[int])
- ``variable`` (Optional[str])
- ``subjectKey`` (Optional[str])
- ``dateCreated`` (Optional[str])
- ``dateModified`` (Optional[str])
- ``queryComments`` (List[imednet.models.queries.QueryComment])

Record Revisions
----------------

**Endpoint:** ``GET /recordRevisions``

**Response Model:**

- ``studyKey`` (Optional[str])
- ``recordRevisionId`` (Optional[int])
- ``recordId`` (Optional[int])
- ``recordRevision`` (Optional[int])
- ``dataRevision`` (Optional[int])
- ``recordStatus`` (Optional[str])
- ``subjectId`` (Optional[int])
- ``subjectKey`` (Optional[str])
- ``siteId`` (Optional[int])
- ``formKey`` (Optional[str])
- ``intervalId`` (Optional[int])
- ``deleted`` (Optional[bool])
- ``dateCreated`` (Optional[str])

Records
-------

**Endpoint:** ``GET /records``

**Response Model:**

- ``studyKey`` (Optional[str])
- ``intervalId`` (Optional[int])
- ``formId`` (Optional[int])
- ``formKey`` (Optional[str])
- ``siteId`` (Optional[int])
- ``recordId`` (Optional[int])
- ``recordOid`` (Optional[str])
- ``recordType`` (Optional[str])
- ``recordStatus`` (Optional[str])
- ``deleted`` (Optional[bool])
- ``dateCreated`` (Optional[str])
- ``dateModified`` (Optional[str])
- ``subjectId`` (Optional[int])
- ``subjectOid`` (Optional[str])
- ``subjectKey`` (Optional[str])
- ``visitId`` (Optional[int])
- ``parentRecordId`` (Optional[int])
- ``recordData`` (Optional[Any])

Sites
-----

**Endpoint:** ``GET /sites``

**Response Model:**

- ``studyKey`` (Optional[str])
- ``siteId`` (Optional[int])
- ``siteName`` (Optional[str])
- ``siteEnrollmentStatus`` (Optional[str])
- ``dateCreated`` (Optional[str])
- ``dateModified`` (Optional[str])

Studies
-------

**Endpoint:** ``GET /``

**Response Model:**

- ``sponsorKey`` (Optional[str])
- ``studyKey`` (Optional[str])
- ``studyId`` (Optional[int])
- ``studyName`` (Optional[str])
- ``studyDescription`` (Optional[str])
- ``studyType`` (Optional[str])
- ``dateCreated`` (Optional[str])
- ``dateModified`` (Optional[str])

Subjects
--------

**Endpoint:** ``GET /subjects``

**Response Model:**

- ``studyKey`` (Optional[str])
- ``subjectId`` (Optional[int])
- ``subjectKey`` (Optional[str])
- ``subjectStatus`` (Optional[str])
- ``siteId`` (Optional[int])
- ``siteName`` (Optional[str])
- ``deleted`` (Optional[bool])
- ``dateCreated`` (Optional[str])
- ``dateModified`` (Optional[str])
- ``keywords`` (Optional[List[imednet.models.subjects.SubjectKeyword]])
- ``enrollmentStartDate`` (Optional[str])

Users
-----

**Endpoint:** ``GET /users``

**Response Model:**

- ``userId`` (Optional[str])
- ``login`` (Optional[str])
- ``firstName`` (Optional[str])
- ``lastName`` (Optional[str])
- ``email`` (Optional[str])
- ``userActiveInStudy`` (Optional[bool])

Variables
---------

**Endpoint:** ``GET /variables``

**Response Model:**

- ``studyKey`` (Optional[str])
- ``variableId`` (Optional[int])
- ``variableType`` (Optional[str])
- ``variableName`` (Optional[str])
- ``sequence`` (Optional[int])
- ``revision`` (Optional[int])
- ``dateCreated`` (Optional[str])
- ``dateModified`` (Optional[str])
- ``formId`` (Optional[int])
- ``formKey`` (Optional[str])
- ``formName`` (Optional[str])
- ``label`` (str | None)
- ``variableOid`` (str | None)

Visits
------

**Endpoint:** ``GET /visits``

**Response Model:**

- ``visitId`` (Optional[int])
- ``studyKey`` (Optional[str])
- ``intervalId`` (Optional[int])
- ``intervalName`` (Optional[str])
- ``subjectId`` (Optional[int])
- ``subjectKey`` (Optional[str])
- ``startDate`` (Optional[str])
- ``endDate`` (Optional[str])
- ``dueDate`` (Optional[str])
- ``visitDate`` (Optional[str])
- ``deleted`` (Optional[bool])
- ``dateCreated`` (Optional[str])
- ``dateModified`` (Optional[str])

