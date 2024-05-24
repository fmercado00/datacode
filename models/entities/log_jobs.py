from pydantic import BaseModel, Field
import datetime

class LogJobs(BaseModel):
    """
    Represents a log class for jobs.
    """
    id: str = Field(default=None)
    job: str = Field(default=None)
    error_message: str = Field(default=None)

