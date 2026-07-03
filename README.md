# imednet

**Unofficial Python SDK for the iMednet clinical trials API.**

Full documentation: <https://fderuiter.github.io/imednet-python-sdk/>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/imednet.svg)](https://pypi.org/project/imednet/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/imednet.svg)](https://pypi.org/project/imednet/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/imednet.svg)](https://pypi.org/project/imednet/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/imednet.svg)](https://pypi.org/project/imednet/)
[![License](https://img.shields.io/pypi/l/imednet.svg)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/fderuiter/imednet-python-sdk/ci.yml?branch=main)](https://github.com/fderuiter/imednet-python-sdk/actions/workflows/ci.yml)

</div>

This package simplifies integration with the iMednet REST API for clinical trial
management. It provides typed endpoint wrappers, helper workflows and a CLI so
researchers and developers can automate data extraction and submission without
reimplementing HTTP logic.

## Documentation

Our documentation is organized according to the **Diátaxis framework**, which categorizes information based on user intent.

### 📚 [Tutorials](docs/tutorials/)
*Learning-oriented guides for getting started.*
- [Quick Start](docs/tutorials/quick_start.rst)
- [Async Quick Start](docs/tutorials/async_quick_start.rst)
- [Examples](docs/tutorials/examples/)

### 🛠️ [How-To Guides](docs/how-to/)
*Problem-oriented guides for completing specific tasks.*
- [CLI Usage](docs/how-to/cli.rst)
- [UAT Workflow](docs/how-to/workflows/uat_workflow.rst)
- [Bulk Submission](docs/how-to/workflows/bulk_submission.rst)
- [Export Destinations](docs/how-to/export_destinations.rst)
- [Streamlit Dashboard](docs/how-to/streamlit_dashboard.md)

### 💡 [Explanation](docs/explanation/)
*Understanding-oriented concepts and architectural overviews.*
- [Architecture](docs/explanation/architecture.rst)
- [API Overview](docs/explanation/api_overview.rst)
- [Plugins System](docs/explanation/plugins.rst)

### 📖 [Reference](docs/reference/)
*Information-oriented material like API documentation and contributor rules.*
- [REST API Reference](docs/reference/rest_api_reference.rst)
- [Configuration](docs/reference/configuration.rst)
- [Contributor Rules](docs/reference/agent_rules.md)
- [Automated API Reference](docs/reference/api/)

## Installation

```bash
# PyPI release
pip install imednet
```

For extended integrations, you can install optional dependencies:
```bash
pip install "imednet[export]"
pip install imednet-workflows
pip install apache-airflow-providers-imednet
pip install imednet-streamlit
```

## Contributing

Contributions are welcome! Please see our [Contributor Guide](AGENTS.md) and [Verification Loop](docs/how-to/verification.md) to get started.

## License

This project is licensed under the MIT license. See [LICENSE](LICENSE) for details.
