from pydantic import BaseModel, Field


class BackupTableRequestModel(BaseModel):
    """
    Represents a request model for backup tables.
    """
    tableName: str = Field(default=None)
