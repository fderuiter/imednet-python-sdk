.. _tlf:

################
TLF Generation
################

The iMednet SDK provides a framework for generating Tables, Listings, and Figures (TLFs) from your clinical trial data. This framework is designed to be extensible, allowing you to create your own custom reports.

.. contents::
   :local:
   :depth: 2

Overview
========

The TLF generation framework is built around the ``TlfReport`` base class. Each specific TLF report is a subclass of this base class and implements the ``generate`` method to produce the report data as a pandas DataFrame.

The SDK provides a command-line interface (CLI) to run these reports.

Creating a new TLF Report
=========================

To create a new TLF report, you need to:

1. Create a new class that inherits from ``imednet.tlf.base.TlfReport``.
2. Implement the ``generate`` method. This method should use the ``self.sdk`` object to fetch the necessary data from the iMednet API and return it as a pandas DataFrame.
3. (Optional) Add a new CLI command to run your report.

Example: Subject Listing
=========================

The SDK includes an example of a subject listing report. Here's how to use it from the CLI:

.. code-block:: bash

    imednet tlf listing subject <your_study_key>

You can also save the output to a CSV file:

.. code-block:: bash

    imednet tlf listing subject <your_study_key> --output-file subject_listing.csv

Here's how you would use it in Python:

.. code-block:: python

    from imednet import ImednetSDK
    from imednet.tlf.listings import SubjectListing

    sdk = ImednetSDK(api_key="...", security_key="...")
    report = SubjectListing(sdk=sdk, study_key="<your_study_key>")
    df = report.generate()
    print(df)
