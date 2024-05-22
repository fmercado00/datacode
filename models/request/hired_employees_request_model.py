from typing import List
from pydantic import BaseModel, Field
import datetime

class HiredEmployeesRequestModel(BaseModel):
    """
    Represents a request model for hired employees.
    """
    id: str = Field(default=None)
    name: str = Field(default=None)
    dateTime: datetime.datetime = Field(default=None)
    departmentId: str = Field(default=None)
    jobId: str= Field(default=None)

class ListHiredEmployeesRequestModel(BaseModel):
    """
    Represents a request model for listing hired employees.
    """
    hiredEmployees: List[HiredEmployeesRequestModel] = Field(default=None)