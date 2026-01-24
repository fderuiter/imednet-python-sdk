import pytest

import imednet.endpoints.sites as sites
from imednet.models.sites import Site


def test_list_requires_study_key(dummy_client, context, paginator_factory, patch_build_filter):
    ep = sites.SitesEndpoint(dummy_client, context)
    paginator_capture = paginator_factory(sites, [{"siteId": 1}])
    patch = patch_build_filter(sites)

    with pytest.raises(KeyError):
        ep.list()

    result = ep.list(study_key="S1", status="ok")

    assert paginator_capture["path"] == "/api/v1/edc/studies/S1/sites"
    assert patch["filters"] == {"status": "ok"}
    assert paginator_capture["params"] == {"filter": "FILTERED"}
    assert isinstance(result[0], Site)


def test_get_not_found(dummy_client, context, paginator_factory):
    ep = sites.SitesEndpoint(dummy_client, context)
    paginator_factory(sites, [])

    with pytest.raises(ValueError):
        ep.get("S1", 1)
