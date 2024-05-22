#FastApi
from fastapi import FastAPI, Body, Query, Path, status, Header, Form, File, UploadFile, Depends, HTTPException, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.request.hired_employees_request_model import HiredEmployeesRequestModel, ListHiredEmployeesRequestModel
from models.response.base_response_model import BaseResponseModel
from service.hired_employees_service import insert_hired_employee



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
def add_hired_employees(listHiredEmployeesRequestModel: ListHiredEmployeesRequestModel) -> BaseResponseModel:
    """
    # Insert Employees
    - Add a list of employees

    ## Parameters:
        - None

    ## Returns:
        - Return Base Response Model

    """
    employeesResponseModel = BaseResponseModel()
    employees_list = listHiredEmployeesRequestModel.hiredEmployees
    if not (1 <= len(employees_list) <= 1000):
        employeesResponseModel.Error = True
        employeesResponseModel.ErrorMessage = "El numero de registros debe estar entre 1 y 1000"
        return employeesResponseModel
    
    employeesResponseModel = insert_hired_employee(employees_list)

    return employeesResponseModel