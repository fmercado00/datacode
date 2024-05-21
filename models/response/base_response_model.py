from pydantic import BaseModel, Field

class BaseResponseModel(BaseModel):
    Error: bool = Field(default=None)
    ErrorMessage: str = Field(default=None)
