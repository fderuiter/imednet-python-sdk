Forms Endpoint
==============

The Forms endpoint returns the design specification for electronic
case report forms (eCRFs) within a study. Each form describes the
questions presented to a subject when a record is created.

Request
-------

``GET /api/v1/edc/studies/{studyKey}/forms``

Query Parameters
----------------

``page``
  Index page to fetch (default ``0``).

``size``
  Items per page (default ``25``, maximum ``500``).

``sort``
  Field to sort by optionally followed by ``asc`` or ``desc``.
  The default is ``formId,asc``.

``filter``
  Optional filter criteria using the syntax described in
  :doc:`../rest_api_reference`.

Example request::

  GET /api/v1/edc/studies/PHARMADEMO/forms?page=0&size=25&sort=formId%2CASC&filter=formId%3D%3D10265

Response
--------

The response contains ``metadata`` and ``pagination`` objects along with a
``data`` array of form records. Each item can be parsed into
:class:`~imednet.models.forms.Form`.

.. code-block::

   {
     "metadata": { "status": "OK", ... },
     "pagination": { "currentPage": 0, "size": 25, "totalPages": 1 },
     "data": [
       {
         "studyKey": "PHARMADEMO",
         "formId": 1,
         "formKey": "FORM_1",
         "formName": "Mock Form 1",
         "formType": "Subject",
         "revision": 1,
         "embeddedLog": false,
         "enforceOwnership": false,
         "userAgreement": false,
         "subjectRecordReport": false,
         "unscheduledVisit": false,
         "otherForms": false,
         "eproForm": false,
         "allowCopy": true,
         "disabled": false,
         "dateCreated": "2025-06-05 21:12:09",
         "dateModified": "2025-06-05 21:12:10"
       }
     ]
   }

Common fields
~~~~~~~~~~~~~

``studyKey``
  Unique study identifier.

``formId``
  Mednet form ID.

``formKey``
  Key used when referencing the form in records.

``formName``
  Human readable name.

``formType``
  eCRF type such as ``Subject`` or ``Site``.

``revision``
  Number of metadata revisions.

``dateCreated``
  Creation timestamp.

``dateModified``
  Last modification timestamp.

Methods
-------

Use :meth:`~imednet.endpoints.forms.FormsEndpoint.list` to
retrieve all forms in a study or :meth:`~imednet.endpoints.forms.FormsEndpoint.get`
to fetch a single form.

`Portal docs <https://portal.prod.imednetapi.com/docs/forms>`_
