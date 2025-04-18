Installation
============

To install the iMednet Python SDK, you can use pip.

**From PyPI (Recommended)**

Once the package is published to the Python Package Index (PyPI), you can install it directly:

.. code-block:: bash

   pip install imednet-python-sdk

**From Source (for development)**

If you want to install directly from the source code repository:

1.  Clone the repository:

    .. code-block:: bash

       git clone https://github.com/FrederickdeRuiter/imednet-python-sdk.git # Replace with actual URL if different
       cd imednet-python-sdk

2.  Install the package in editable mode (recommended for development):

    .. code-block:: bash

       pip install -e .

   Alternatively, build and install:

   .. code-block:: bash

      pip install .

**Dependencies**

The SDK relies on the following core libraries (see `pyproject.toml` or `requirements.txt` for specific version constraints):

*   `requests`: For making HTTP requests.
*   `pydantic`: For data modeling and validation.
