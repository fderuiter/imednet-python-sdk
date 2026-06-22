"""TODO: Add docstring."""


def test_smoke_import() -> None:
    """TODO: Add docstring."""
    import imednet

    assert hasattr(imednet, "ImednetSDK")


def test_orchestration_exports() -> None:
    """TODO: Add docstring."""
    from imednet import (
        FilterConflictError,
        MultiStudyOrchestrator,
        OrchestratorError,
        OrchestratorResult,
        StudyWorkerCallable,
    )

    assert MultiStudyOrchestrator.__name__ == "MultiStudyOrchestrator"
    assert OrchestratorResult.__name__ == "OrchestratorResult"
    assert StudyWorkerCallable.__name__ == "StudyWorkerCallable"
    assert OrchestratorError.__name__ == "OrchestratorError"
    assert FilterConflictError.__name__ == "FilterConflictError"


def test_role_import() -> None:
    """TODO: Add docstring."""
    from imednet.models import Role

    assert Role.__name__ == "Role"
