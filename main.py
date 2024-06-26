#FastApi
from fastapi import FastAPI, Body, Query, Path, status, Header, Form, File, UploadFile, Depends, HTTPException, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2AuthorizationCodeBearer

from models.request.backup_request_model import BackupTableRequestModel
from models.request.departments_request_model import ListDepartmentRequestModel
from models.request.hired_employees_request_model import HiredEmployeesRequestModel, ListHiredEmployeesRequestModel
from models.request.jobs_request_model import ListJobRequestModel
from models.response.base_response_model import BaseResponseModel
from security.okta import OktaJWTValidator
from service.backup_service import BackupService
from service.departments_service import insert_departments
from service.hired_employees_service import insert_hired_employee
from security.keyvault import KeyVaultSecrets
from service.jobs_service import insert_jobs
from service.restore_service import RestoreService


app = FastAPI()

key_vault_name = "ServicesDbKeyVault"
key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"
key_vault_secrets = KeyVaultSecrets(vault_url=key_vault_uri)

OKTA_CLIENT_ID = key_vault_secrets.get_secret("OKTACLIENTID")
OKTA_CLIENT_SECRET = key_vault_secrets.get_secret("OKTACLIENTSECRET")
OkTA_ISSUER = key_vault_secrets.get_secret("OKTAISSUER")

validator = OktaJWTValidator(OkTA_ISSUER)
oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="", tokenUrl="")

def validate_token(token: str = Depends(oauth2_scheme)):
    return validator.validate_token(token)


@app.get("/")
async def read_root(user: dict = Depends(validate_token)):
    return {"App": "Alive!"}

@app.post(
    path="/v1/employees/add",
    response_model=BaseResponseModel,
    status_code=status.HTTP_200_OK,
    tags=["Employees"],
    )
def add_hired_employees(listHiredEmployeesRequestModel: ListHiredEmployeesRequestModel, user: dict = Depends(validate_token)) -> BaseResponseModel:
    """
    # Insert Employees
    - Add a list of employees

    ## Parameters:
        - ListHiredEmployees Request Model

    ## Returns:
        - Return Base Response Model

    """
    response = BaseResponseModel()
    employees_list = listHiredEmployeesRequestModel.hiredEmployees
    if not (1 <= len(employees_list) <= 1000):
        response.Error = True
        response.ErrorMessage = "El numero de registros debe estar entre 1 y 1000"
        return response
    
    response = insert_hired_employee(employees_list)

    return response


@app.post(
    path="/v1/jobs/add",
    response_model=BaseResponseModel,
    status_code=status.HTTP_200_OK,
    tags=["Jobs"],
    )
def add_jobs(listJobsRequestModel: ListJobRequestModel, user: dict = Depends(validate_token)) -> BaseResponseModel:
    """
    # Insert Jobs
    - Add a list of jobs

    ## Parameters:
        - ListJobRequestModel Request Model

    ## Returns:
        - Return Base Response Model

    """
    response = BaseResponseModel()
    jobs_list = listJobsRequestModel.jobs
    if not (1 <= len(jobs_list) <= 1000):
        response.Error = True
        response.ErrorMessage = "El numero de registros debe estar entre 1 y 1000"
        return response
    
    response = insert_jobs(jobs_list)

    return response



@app.post(
    path="/v1/departments/add",
    response_model=BaseResponseModel,
    status_code=status.HTTP_200_OK,
    tags=["Departments"],
    )
def add_department(listDepartmentsRequestModel: ListDepartmentRequestModel, user: dict = Depends(validate_token)) -> BaseResponseModel:
    """
    # Insert Departments
    - Add a list of departments

    ## Parameters:
        - ListDepartmentRequestModel Request Model

    ## Returns:
        - Return Base Response Model

    """
    response = BaseResponseModel()
    departments_list = listDepartmentsRequestModel.departments
    if not (1 <= len(departments_list) <= 1000):
        response.Error = True
        response.ErrorMessage = "El numero de registros debe estar entre 1 y 1000"
        return response
    
    response = insert_departments(departments_list)

    return response


@app.post(
    path="/v1/maintenance/backup",
    response_model=BaseResponseModel,
    status_code=status.HTTP_200_OK,
    tags=["Maintenance"],
    )
def backup_tables(backup_table_request_model: BackupTableRequestModel, user: dict = Depends(validate_token)) -> BaseResponseModel:
    """
    # Backup Table
    - Copy the data from a table to a file and upload it to a blob storage

    ## Parameters:
        - Backup Table Request Model

    ## Returns:
        - Return Base Response Model

    """
    response = BaseResponseModel()
    response.Error = False
    response.ErrorMessage = ""


    db_connection = key_vault_secrets.get_secret("DATABASEURI1")
    dl_connection = key_vault_secrets.get_secret("DataCodeDLConnectionString")
    container_name = 'backups'

    backup_service = BackupService(db_connection,dl_connection,container_name)
    response = backup_service.backup_table_to_blob(backup_table_request_model.tableName)

    return response

@app.post(
    path="/v1/maintenance/restore",
    response_model=BaseResponseModel,
    status_code=status.HTTP_200_OK,
    tags=["Maintenance"],
    )
def restore_tables(backup_table_request_model: BackupTableRequestModel, user: dict = Depends(validate_token)) -> BaseResponseModel:
    """
    # Restore Table
    - Copy the data from an avro to a table
    ## Parameters:
        - Backup Table Request Model

    ## Returns:
        - Return Base Response Model

    """
    response = BaseResponseModel()
    response.Error = False
    response.ErrorMessage = ""

    db_connection = key_vault_secrets.get_secret("DATABASEURI1")
    dl_connection = key_vault_secrets.get_secret("DataCodeDLConnectionString")
    container_name = 'backups'

    restore_service = RestoreService(db_connection,dl_connection,container_name)
    response = restore_service.restore_table_from_blob(backup_table_request_model.tableName)

    return response

