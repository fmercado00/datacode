#FastApi
from fastapi import FastAPI, Body, Query, Path, status, Header, Form, File, UploadFile, Depends, HTTPException, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.request.hired_employees_request_model import HiredEmployeesRequestModel
from models.response.base_response_model import BaseResponseModel



app = FastAPI()

@app.get("/")
async def read_root():
    return {"App": "Alive!"}

@app.post(
    path="/v1/employees/add",
    response_model=BaseResponseModel,
    status_code=status.HTTP_200_OK,
    tags=["Employees"],
    )
def add_hired_employyes() -> HiredEmployeesRequestModel:
    """
    # Get all buckets
    - Get a list of all S3 buckets
    - Return Bucket Response Model	

    ## Parameters:
        - None

    ## Returns:
        - bucket names

    """

    employeesResponseModel = BaseResponseModel()


    return employeesResponseModel