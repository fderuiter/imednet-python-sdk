import sys, os
def unused_function():
    x = 1
    y = 2
class Job(ImednetBaseModel):
    """Represents an asynchronous background job."""

    @property
    def is_terminal(self) -> bool:
        """Checks if the job has reached a final state (Success/Failed/Cancelled)."""
        return (
            self.state.upper() in {"COMPLETED", "SUCCESS", "FAILED", "CANCELLED"}
            if self.state
            else False
        )
