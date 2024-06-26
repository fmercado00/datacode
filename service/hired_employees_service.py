import json
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import datetime
import re
from logger.logger import AzureBlobLogger
from models.entities.log_hired_employee import LogHiredEmployees
from models.request.hired_employees_request_model import HiredEmployeesRequestModel
from models.response.base_response_model import BaseResponseModel
from security.keyvault import KeyVaultSecrets
import pydantic

key_vault_name = "ServicesDbKeyVault"
key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"
key_vault_secrets = KeyVaultSecrets(vault_url=key_vault_uri)

db_connection = key_vault_secrets.get_secret("DATABASEURI1")
dl_connection = key_vault_secrets.get_secret("DataCodeDLConnectionString")
container_name = 'logger'

engine = create_engine(db_connection)

Base = declarative_base()

class HiredEmployees(Base):
    """
    Represents a hired employee.

    Attributes:
        id (int): The unique identifier for the employee.
        name (str): The name of the employee.
        datetime (datetime.date): The date and time when the employee was hired.
        department_id (int): The ID of the department the employee belongs to.
        job_id (int): The ID of the job the employee is assigned to.
    """
    __tablename__ = 'hired_employees'
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False)
    datetime = Column(Date, nullable=False)
    department_id = Column(Integer, nullable=False)
    job_id = Column(Integer, nullable=False)



def valitate_hired_employee(hiredEmployee: HiredEmployeesRequestModel) -> bool:
    """
    Validates the hired employee data.

    Args:
        hiredEmployee (HiredEmployeesRequestModel): The hired employee object to be validated.

    Returns:
        bool: False if the hired employee data is valid, True otherwise.
    """
    if hiredEmployee.id is None:
        return True, "El campo id es requerido"
    if hiredEmployee.name is None:
        return True, "El campo name es requerido"
    if hiredEmployee.dateTime is None:
        return True,  "El campo dateTime es requerido"
    if hiredEmployee.departmentId is None:
        return True, "El campo departmentId es requerido"
    if hiredEmployee.jobId is None:
        return True, "El campo jobId es requerido"
    if not re.match(r'^[a-zA-Z0-9 ]+$', hiredEmployee.name):
        return True, "El campo name solo puede contener letras y numeros"
    if not re.match(r'^[0-9 ]+$', hiredEmployee.id):
        return True, "El campo id solo puede contener numeros"
    if not re.match(r'^[0-9 ]+$', hiredEmployee.departmentId):
        return True, "El campo departmentId solo puede contener numeros"
    if not re.match(r'^[0-9 ]+$', hiredEmployee.jobId):
        return True, "El campo jobId solo puede contener numeros"
    return False, ""


def log_invalid_employee(listLogHiredEmployees: List[LogHiredEmployees]) -> BaseResponseModel:
    """
    Logs the list of hired employees to an Azure Blob Storage container.

    Args:
        listLogHiredEmployees (List[LogHiredEmployees]): A list of hired employees.

    Returns:
        BaseResponseModel: The response model indicating the success or failure of the logging operation.
    """
    response = BaseResponseModel()
    response.Error = False
    response.ErrorMessage = ""
    try:
        azure_blob_logger = AzureBlobLogger(dl_connection, container_name)
        timestamp = datetime.datetime.now().isoformat()
        log_blob_name = f'log_hired_employees_{timestamp}.log'
        hired_employees_json = '[' + ','.join([emp.model_dump_json() for emp in listLogHiredEmployees]) + ']'
        azure_blob_logger.log_data(hired_employees_json, log_blob_name)
        response.Error = True
        response.ErrorMessage = "El proceso detecto registros invalidos, se genero un log con los registros."
    except Exception as e:
        response.Error = True
        response.ErrorMessage = str(e)
    return response


def insert_hired_employee(listLogHiredEmployees: List[HiredEmployeesRequestModel]) -> BaseResponseModel:
    """
    Inserts a list of hired employees into the database.

    Args:
        listLogHiredEmployees (List[HiredEmployeesRequestModel]): A list of HiredEmployeesRequestModel objects representing the hired employees to be inserted.

    Returns:
        BaseResponseModel: A BaseResponseModel object indicating the success or failure of the operation.

    """
    response = BaseResponseModel()
    
    Session = sessionmaker(bind=engine)
    session = Session()
    log_list : List[LogHiredEmployees] = []
    exists_validation_error = False
    enable_log = False
    for hiredEmployee in listLogHiredEmployees:
        exists_validation_error, error_validation_message = valitate_hired_employee(hiredEmployee)
        if exists_validation_error:
            log_list = add_employee_to_log(log_list, hiredEmployee, error_validation_message)
            enable_log = True
        else:
            new_employee = HiredEmployees(
                id=hiredEmployee.id,
                name=hiredEmployee.name,
                datetime=hiredEmployee.dateTime,
                department_id=hiredEmployee.departmentId,
                job_id=hiredEmployee.jobId
            )

            try:
                session.add(new_employee)
                session.commit()
                response.Error = False
                response.ErrorMessage = "Los registros se insertaron correctamente"
            except IntegrityError as e: 
                session.rollback()
                result = set_specific_error_message(str(e.orig))
                log_list = add_employee_to_log(log_list, hiredEmployee, result.ErrorMessage)
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
        log_response = log_invalid_employee(log_list)
        response.Error = log_response.Error
        response.ErrorMessage = log_response.ErrorMessage
    return response
    
def add_employee_to_log(log_list: List[LogHiredEmployees], hiredEmployee: HiredEmployeesRequestModel, error_validation_message: str) -> List[LogHiredEmployees]:
    log_employee = LogHiredEmployees()
    log_employee.id=hiredEmployee.id
    log_employee.name=hiredEmployee.name
    log_employee.dateTime=hiredEmployee.dateTime
    log_employee.departmentId=hiredEmployee.departmentId
    log_employee.jobId=hiredEmployee.jobId
    log_employee.error_message=error_validation_message
    log_list.append(log_employee)
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







