from typing import List
from pydantic import BaseModel, Field


class DepartmentRequestModel(BaseModel):
    """
    Represents a request model for departments.
    """
    id: str = Field(default=None)
    department: str = Field(default=None)

class ListDepartmentRequestModel(BaseModel):
    """
    Represents a request model for listing departments.
    """
    departments: List[DepartmentRequestModel] = Field(default=None)