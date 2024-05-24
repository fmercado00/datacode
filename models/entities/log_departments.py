from pydantic import BaseModel, Field
import datetime

class LogDepartments(BaseModel):
    """
    Represents a log class for departments.
    """
    id: str = Field(default=None)
    department: str = Field(default=None)
    error_message: str = Field(default=None)

