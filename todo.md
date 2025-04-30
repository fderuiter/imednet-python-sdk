# TODO List

1. **Add Async Support**
   * Implement an `AsyncClient` using `httpx`'s async capabilities alongside the synchronous client.
   * Ensure relevant workflows and examples are updated or created for async usage.

2. **Assess and Ensure API Completeness**
   * Perform a thorough review comparing the SDK against the official iMedNet API documentation.
   * Identify and implement any missing endpoints, parameters, or functionalities.

3. **Expand Workflows & CLI**
   * Identify common multi-step iMedNet tasks not yet covered by `imednet.workflows`.
   * Implement new workflows to simplify these tasks for users.
   * Expand the `cli.py` interface with more commands corresponding to SDK features and workflows.

4. **Enhance Documentation**
   * Improve the Sphinx documentation (`docs/`) with more detailed explanations, tutorials, and usage examples.
   * Ensure the API reference documentation is complete and auto-generated correctly.
   * Add more practical examples to `imednet/examples/`.

5. **Community & Maintenance**
   * Actively encourage community contributions as outlined in `CONTRIBUTING.md`.
   * Establish a regular process for reviewing dependencies (`poetry show --outdated`) for updates or vulnerabilities.
   * Monitor upstream iMedNet API changes and plan for SDK updates accordingly.
