import re

with open("src/imednet/sdk_convenience.py", "r") as f:
    content = f.read()

# We want to keep create_record, poll_job, async_poll_job as they have different signatures,
# but we will replace all the get_ methods.

start_marker = "    def get_studies(self: SDKProtocol, **filters: Any) -> List[Study]:"
if start_marker in content:
    pre = content.split(start_marker)[0]

    # create the new getattr logic
    new_methods = """    def __getattr__(self, name: str) -> Any:
        \"\"\"
        Dynamically resolve get_* methods to their corresponding endpoint list() or get() calls.
        \"\"\"
        if name.startswith("get_"):
            target_name = name[4:]

            # Special case for get_job
            if target_name == "job":
                def _get_job_wrapper(study_key: str, batch_id: str) -> JobStatus:
                    return self.jobs.get(study_key, batch_id)  # type: ignore
                return _get_job_wrapper

            # Special case for record_revisions
            if target_name == "record_revisions":
                target_endpoint = self.record_revisions  # type: ignore
            else:
                target_endpoint = getattr(self, target_name, None)

            if target_endpoint is not None and hasattr(target_endpoint, "list"):
                def _list_wrapper(*args: Any, **kwargs: Any) -> Any:
                    return target_endpoint.list(*args, **kwargs)
                return _list_wrapper

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def create_record(
        self: SDKProtocol,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,
    ) -> Job:
        \"\"\"Create records in the specified study.\"\"\"
        return self.records.create(
            study_key,
            records_data,
            email_notify=email_notify,
        )

    def poll_job(
        self: SDKProtocol,
        study_key: str,
        batch_id: str,
        *,
        interval: int = 5,
        timeout: int = 300,
    ) -> JobStatus:
        \"\"\"Poll a job until it reaches a terminal state.\"\"\"

        return JobPoller(self.jobs.get, False).run(study_key, batch_id, interval, timeout)

    async def async_poll_job(
        self: SDKProtocol,
        study_key: str,
        batch_id: str,
        *,
        interval: int = 5,
        timeout: int = 300,
    ) -> JobStatus:
        \"\"\"Asynchronously poll a job until it reaches a terminal state.\"\"\"

        return await JobPoller(self.jobs.async_get, True).run_async(
            study_key, batch_id, interval, timeout
        )
"""
    with open("src/imednet/sdk_convenience.py", "w") as f:
        f.write(pre + new_methods)
    print("Patched successfully")
else:
    print("Start marker not found")
