imednet.discovery module
========================

Runtime helpers that locate study metadata for tests and scripts.
When required identifiers are not provided, these utilities query the
first available study, form, site, subject, or interval.


discover_study_key
------------------

.. function:: discover_study_key(sdk: ImednetSDK) -> str

   Return the first study key available for the provided SDK.

   :param sdk: Authenticated :class:`~imednet.sdk.ImednetSDK` instance.
   :return: Study key of the first available study.
   :raises imednet.discovery.NoLiveDataError: When no studies exist.

   .. code-block:: python

      from imednet import ImednetSDK
      from imednet.discovery import discover_study_key

      sdk = ImednetSDK(base_url, (username, token))
      study_key = discover_study_key(sdk)


discover_form_key
-----------------

.. function:: discover_form_key(sdk: ImednetSDK, study_key: str) -> str

   Return the first subject record form key for ``study_key``.

   :param sdk: Authenticated SDK.
   :param study_key: Identifier of the study to query.
   :return: First form key supporting subject records.
   :raises imednet.discovery.NoLiveDataError: When no suitable forms exist.

   .. code-block:: python

      form_key = discover_form_key(sdk, study_key)


discover_site_name
------------------

.. function:: discover_site_name(sdk: ImednetSDK, study_key: str) -> str

   Return the first active site name for ``study_key``.

   :param sdk: Authenticated SDK.
   :param study_key: Identifier of the study to query.
   :return: Name of the first active site.
   :raises imednet.discovery.NoLiveDataError: When no active sites exist.

   .. code-block:: python

      site_name = discover_site_name(sdk, study_key)


discover_subject_key
--------------------

.. function:: discover_subject_key(sdk: ImednetSDK, study_key: str) -> str

   Return the first active subject key for ``study_key``.

   :param sdk: Authenticated SDK.
   :param study_key: Identifier of the study to query.
   :return: Key for the first active subject.
   :raises imednet.discovery.NoLiveDataError: When no active subjects exist.

   .. code-block:: python

      subject_key = discover_subject_key(sdk, study_key)


discover_interval_name
----------------------

.. function:: discover_interval_name(sdk: ImednetSDK, study_key: str) -> str

   Return the first non-disabled interval name for ``study_key``.

   :param sdk: Authenticated SDK.
   :param study_key: Identifier of the study to query.
   :return: Name of the first active interval.
   :raises imednet.discovery.NoLiveDataError: When no active intervals exist.

   .. code-block:: python

      interval_name = discover_interval_name(sdk, study_key)

