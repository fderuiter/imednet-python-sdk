# apache-airflow-providers-imednet

This is the apache-airflow-providers-imednet package. It provides an integration between Apache Airflow and the iMednet SDK.

## Using the ImednetHook

The `ImednetHook` allows you to interact with the iMednet system securely by resolving configurations from Airflow connections. It provides access to the underlying `ImednetSDK` client.

### Getting the SDK Client (Modern Approach)

To retrieve a configured SDK client to use in your custom operators or tasks, use the `get_sdk_client()` method:

```python
from apache_airflow_providers_imednet.hooks import ImednetHook

def my_task_logic():
    hook = ImednetHook(imednet_conn_id="imednet_default")
    sdk_client = hook.get_sdk_client()
    
    # Use the sdk_client to interact with iMednet
    studies = sdk_client.studies.list()
```

### Deprecation Notice: `get_conn()`

The legacy connection helper `ImednetHook.get_conn()` is **deprecated** and will be removed in a future release. Calling this method will now emit a standard Python `DeprecationWarning` to the logs.

#### Transitioning to the Modern Client

If you have legacy DAGs or custom operators using `get_conn()`, please update them to use `get_sdk_client()` instead. Both methods return the same `ImednetSDK` client, making the migration straightforward:

**Before (Deprecated):**
```python
client = hook.get_conn()
```

**After (Recommended):**
```python
client = hook.get_sdk_client()
```
