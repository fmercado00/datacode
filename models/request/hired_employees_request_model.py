from pydantic import BaseModel, Field
import datetime

class HiredEmployeesRequestModel(BaseModel):
    id: int = Field(default=None)
    name: str = Field(default=None)
    dateTime: datetime.datetime = Field(default=None)
    departmentId: int = Field(default=None)
    jobId: int= Field(default=None)