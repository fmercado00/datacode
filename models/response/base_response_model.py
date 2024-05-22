from pydantic import BaseModel, Field

class BaseResponseModel(BaseModel):
    """
    Base class for response models.
    """
    Error: bool = Field(default=None)
    ErrorMessage: str = Field(default=None)
