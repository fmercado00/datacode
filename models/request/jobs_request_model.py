from typing import List
from pydantic import BaseModel, Field


class JobRequestModel(BaseModel):
    """
    Represents a request model for jobs.
    """
    id: str = Field(default=None)
    job: str = Field(default=None)

class ListJobRequestModel(BaseModel):
    """
    Represents a request model for listing jobs.
    """
    jobs: List[JobRequestModel] = Field(default=None)