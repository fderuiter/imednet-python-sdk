"""Endpoint for checking job status in a study."""

from imednet.core.paginator import AsyncSimpleListPaginator, SimpleListPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.mixins import DirectGetMixin, ListMixin
from imednet.models.jobs import Job, JobStatus


class JobsEndpoint(ListMixin[Job], DirectGetMixin[Job], BaseEndpoint):
    """
    API endpoint for retrieving status and details of jobs in an iMedNet study.

    Provides a method to fetch a job by its batch ID.
    """

    PATH = "jobs"
    MODEL = Job
    GET_MODEL = JobStatus
    paginator_cls = SimpleListPaginator
    async_paginator_cls = AsyncSimpleListPaginator
