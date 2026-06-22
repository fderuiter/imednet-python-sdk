"""TODO: Add docstring."""
from imednet.sdk import ImednetSDK


def test_get_studies(sdk: ImednetSDK) -> None:
    """TODO: Add docstring."""
    assert sdk.get_studies()


def test_get_records(sdk: ImednetSDK, study_key: str) -> None:
    """TODO: Add docstring."""
    records = sdk.get_records(study_key)
    assert isinstance(records, list)


def test_get_sites(sdk: ImednetSDK, study_key: str) -> None:
    """TODO: Add docstring."""
    sites = sdk.get_sites(study_key)
    assert isinstance(sites, list)


def test_get_subjects(sdk: ImednetSDK, study_key: str) -> None:
    """TODO: Add docstring."""
    subjects = sdk.get_subjects(study_key)
    assert isinstance(subjects, list)


def test_get_forms(sdk: ImednetSDK, study_key: str) -> None:
    """TODO: Add docstring."""
    forms = sdk.get_forms(study_key)
    assert isinstance(forms, list)


def test_get_intervals(sdk: ImednetSDK, study_key: str) -> None:
    """TODO: Add docstring."""
    intervals = sdk.get_intervals(study_key)
    assert isinstance(intervals, list)


def test_get_variables(sdk: ImednetSDK, study_key: str) -> None:
    """TODO: Add docstring."""
    vars_ = sdk.get_variables(study_key)
    assert isinstance(vars_, list)


def test_get_visits(sdk: ImednetSDK, study_key: str) -> None:
    """TODO: Add docstring."""
    visits = sdk.get_visits(study_key)
    assert isinstance(visits, list)


def test_get_codings(sdk: ImednetSDK, study_key: str) -> None:
    """TODO: Add docstring."""
    codings = sdk.get_codings(study_key)
    assert isinstance(codings, list)


def test_get_queries(sdk: ImednetSDK, study_key: str) -> None:
    """TODO: Add docstring."""
    queries = sdk.get_queries(study_key)
    assert isinstance(queries, list)


def test_get_record_revisions(sdk: ImednetSDK, study_key: str) -> None:
    """TODO: Add docstring."""
    revs = sdk.get_record_revisions(study_key)
    assert isinstance(revs, list)


def test_get_users(sdk: ImednetSDK, study_key: str) -> None:
    """TODO: Add docstring."""
    users = sdk.get_users(study_key)
    assert isinstance(users, list)


def test_get_job(sdk: ImednetSDK, study_key: str, generated_batch_id: str) -> None:
    """TODO: Add docstring."""
    job = sdk.get_job(study_key, generated_batch_id)
    assert job.batch_id == generated_batch_id


def test_poll_job(sdk: ImednetSDK, study_key: str, generated_batch_id: str) -> None:
    """TODO: Add docstring."""
    job = sdk.poll_job(study_key, generated_batch_id, interval=1, timeout=60)
    assert job.batch_id == generated_batch_id
