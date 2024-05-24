from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import datetime
import re
from logger.logger import AzureBlobLogger

from models.entities.log_departments import LogDepartments
from models.request.departments_request_model import DepartmentRequestModel
from models.response.base_response_model import BaseResponseModel
from security.keyvault import KeyVaultSecrets


key_vault_name = "ServicesDbKeyVault"
key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"
key_vault_secrets = KeyVaultSecrets(vault_url=key_vault_uri)

db_connection = key_vault_secrets.get_secret("DATABASEURI1")
dl_connection = key_vault_secrets.get_secret("DataCodeDLConnectionString")
container_name = 'logger'

engine = create_engine(db_connection)

Base = declarative_base()

class Departments(Base):
    """
    Represents a department.

    Attributes:
        id (int): The unique identifier for the department.
        department (str): The name of the department.
    """
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, autoincrement=False)
    department = Column(String, nullable=False)



def valitate_departments(department: DepartmentRequestModel) -> bool:
    """
    Validates the depertment data.

    Args:
        job (DepartmentsRequestModel): The hired employee object to be validated.

    Returns:
        bool: False if the hired employee data is valid, True otherwise.
    """
    if department.id is None:
        return True, "El campo id es requerido"
    if department.department is None:
        return True, "El campo department es requerido"
    
    if not re.match(r'^[a-zA-Z0-9 ]+$', department.department):
        return True, "El campo department solo puede contener letras y numeros"
    if not re.match(r'^[0-9 ]+$', department.id):
        return True, "El campo id solo puede contener numeros"
    
    return False, ""


def log_invalid_departments(listLogDepartments: List[LogDepartments]) -> BaseResponseModel:
    """
    Logs the list of departments to an Azure Blob Storage container.

    Args:
        listLogDepartments (List[LogDepartments]): A list of departments.

    Returns:
        BaseResponseModel: The response model indicating the success or failure of the logging operation.
    """
    response = BaseResponseModel()
    response.Error = False
    response.ErrorMessage = ""
    try:
        azure_blob_logger = AzureBlobLogger(dl_connection, container_name)
        timestamp = datetime.datetime.now().isoformat()
        log_blob_name = f'departments_{timestamp}.log'
        departments_json = '[' + ','.join([dep.model_dump_json() for dep in listLogDepartments]) + ']'
        azure_blob_logger.log_data(departments_json, log_blob_name)
        response.Error = True
        response.ErrorMessage = "El proceso detecto registros invalidos, se genero un log con los registros."
    except Exception as e:
        response.Error = True
        response.ErrorMessage = str(e)
    return response


def insert_departments(listLogDepartments: List[DepartmentRequestModel]) -> BaseResponseModel:
    """
    Inserts a list of departments into the database.

    Args:
        listLogDepartments (List[DepartmentsRequestModel]): A list of DepartmentsRequestModel objects representing the jobs to be inserted.

    Returns:
        BaseResponseModel: A BaseResponseModel object indicating the success or failure of the operation.

    """
    response = BaseResponseModel()
    
    Session = sessionmaker(bind=engine)
    session = Session()
    log_list : List[LogDepartments] = []
    exists_validation_error = False
    enable_log = False
    for department in listLogDepartments:
        exists_validation_error, error_validation_message = valitate_departments(department)
        if exists_validation_error:
            log_list = add_department_to_log(log_list, department, error_validation_message)
            enable_log = True
        else:
            new_department = Departments(
                id=department.id,
                department=department.department,
            )

            try:
                session.add(new_department)
                session.commit()
                response.Error = False
                response.ErrorMessage = "Los registros se insertaron correctamente"
            except IntegrityError as e: 
                session.rollback()
                result = set_specific_error_message(str(e.orig))
                log_list = add_department_to_log(log_list, department, result.ErrorMessage)
                enable_log = True
                response.Error = result.Error
                response.ErrorMessage = result.ErrorMessage
            except Exception as e:
                session.rollback()
                enable_log = True
                response.Error = True
                response.ErrorMessage = str(e)
            finally:
                session.close()

    if enable_log:
        log_response = log_invalid_departments(log_list)
        response.Error = log_response.Error
        response.ErrorMessage = log_response.ErrorMessage
    return response
    
def add_department_to_log(log_list: List[LogDepartments], department: DepartmentRequestModel, error_validation_message: str) -> List[LogDepartments]:
    log_departments = LogDepartments()
    log_departments.id=department.id
    log_departments.department=department.department
    log_departments.error_message=error_validation_message
    log_list.append(log_departments)
    return log_list


def set_specific_error_message(error_message: str) -> BaseResponseModel:
    """
    Sets a specific error message in the response model.

    Args:
        response (BaseResponseModel): The response model to be updated.
        error_message (str): The error message to be set in the response model.

    Returns:
        BaseResponseModel: The response model with the updated error message.
    """
    response = BaseResponseModel()
    response.Error = True
    if 'FK_hired_employees_jobs' in error_message:
        response.ErrorMessage = "El job id no existe en el catálogo."
    elif 'FK_hired_employees_departments' in error_message:
        response.ErrorMessage = "El department id no existe en el catálogo."
    elif "PRIMARY KEY constraint" in error_message:
        response.ErrorMessage = "El id ya existe en la tabla"
    else:
        response.ErrorMessage = error_message
    return response







