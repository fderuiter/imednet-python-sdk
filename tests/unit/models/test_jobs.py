from datetime import datetime

from imednet.models.jobs import Job


def test_job_creation_with_field_names():
    now = datetime.now()
    job = Job(
        job_id="test_job",
        batch_id="test_batch",
        state="running",
        date_created=now,
        date_started=now,
        date_finished=now,
    )
    assert job.job_id == "test_job"
    assert job.batch_id == "test_batch"
    assert job.state == "running"
    assert job.date_created == now
    assert job.date_started == now
    assert job.date_finished == now


def test_job_creation_with_aliases():
    now = datetime.now()
    job = Job(
        jobId="test_job",
        batchId="test_batch",
        state="running",
        dateCreated=now,
        dateStarted=now,
        dateFinished=now,
    )
    assert job.job_id == "test_job"
    assert job.batch_id == "test_batch"
    assert job.state == "running"
    assert job.date_created == now
    assert job.date_started == now
    assert job.date_finished == now


def test_job_from_json():
    test_data = {
        "jobId": "test_job",
        "batchId": "test_batch",
        "state": "complete",
        "dateCreated": "2023-01-01T12:00:00",
        "dateStarted": "2023-01-01T12:00:00",
        "dateFinished": "2023-01-01T13:00:00",
    }
    job = Job.from_json(test_data)
    assert job.job_id == "test_job"
    assert job.batch_id == "test_batch"
    assert job.state == "complete"
    assert isinstance(job.date_created, datetime)
    assert isinstance(job.date_started, datetime)
    assert isinstance(job.date_finished, datetime)


def test_empty_job():
    job = Job()
    assert job.job_id == ""
    assert job.batch_id == ""
    assert job.state == ""
    assert isinstance(job.date_created, datetime)
    assert isinstance(job.date_started, datetime)
    assert isinstance(job.date_finished, datetime)
