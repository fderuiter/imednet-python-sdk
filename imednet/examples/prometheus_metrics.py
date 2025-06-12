"""Example showing how to expose Prometheus metrics."""

from imednet.sdk import ImednetSDK

api_key = "XXXXXXXXXX"
security_key = "XXXXXXXXXX"

sdk = ImednetSDK(api_key=api_key, security_key=security_key, enable_metrics=True)

try:
    sdk.studies.list()
    print("Metrics server running on http://localhost:8000")
except Exception as e:
    print(f"Error: {e}")
