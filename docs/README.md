# Metrics

The SDK can optionally expose Prometheus metrics for API calls. Install the `metrics` extra and enable metrics when creating the SDK.

```bash
pip install "imednet-python-sdk[metrics]"
```

```python
from imednet.sdk import ImednetSDK

sdk = ImednetSDK(
    api_key="KEY",
    security_key="SEC",
    enable_metrics=True,
    metrics_port=8000,
)
```

Metrics will be available at `http://localhost:8000/`.
