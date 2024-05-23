import json
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import re
from logger.logger import AzureBlobLogger
from models.request.hired_employees_request_model import HiredEmployeesRequestModel
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


def to_dict(obj):
    data = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    if 'datetime' in data and isinstance(data['datetime'], (datetime.date, datetime.datetime)):
        data['datetime'] = data['datetime'].isoformat()  # Convertir datetime a string
    return data


def valitate_hired_employee(hiredEmployee: HiredEmployeesRequestModel) -> bool:
    """
    Validates the hired employee data.

    Args:
        hiredEmployee (HiredEmployeesRequestModel): The hired employee object to be validated.

    Returns:
        bool: True if the hired employee data is valid, False otherwise.
    """
    if hiredEmployee.id is None:
        return False
    if hiredEmployee.name is None:
        return False
    if hiredEmployee.dateTime is None:
        return False
    if hiredEmployee.departmentId is None:
        return False
    if hiredEmployee.jobId is None:
        return False
    if not re.match(r'^[a-zA-Z0-9 ]+$', hiredEmployee.name):
        return False
    if not re.match(r'^[0-9 ]+$', hiredEmployee.id):
        return False
    if not re.match(r'^[0-9 ]+$', hiredEmployee.departmentId):
        return False
    if not re.match(r'^[0-9 ]+$', hiredEmployee.jobId):
        return False
    return True


def log_invalid_employee(listHiredEmployees: List[HiredEmployees]) -> BaseResponseModel:
    """
    Logs the list of hired employees to an Azure Blob Storage container.

    Args:
        listHiredEmployees (List[HiredEmployeesRequestModel]): A list of hired employees.

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
        hired_employees_json = json.dumps([to_dict(emp) for emp in listHiredEmployees], separators=(',', ':'))
        azure_blob_logger.log_data(hired_employees_json, log_blob_name)
        response.Error = True
        response.ErrorMessage = "El proceso detecto registros invalidos, se genero un log con los registros invalidos"
    except Exception as e:
        response.Error = True
        response.ErrorMessage = str(e)
    return response


def insert_hired_employee(listHiredEmployees: List[HiredEmployeesRequestModel]) -> BaseResponseModel:
    """
    Inserts a list of hired employees into the database.

    Args:
        listHiredEmployees (List[HiredEmployeesRequestModel]): A list of HiredEmployeesRequestModel objects representing the hired employees to be inserted.

    Returns:
        BaseResponseModel: A BaseResponseModel object indicating the success or failure of the operation.

    """
    response = BaseResponseModel()
    response.Error = False
    response.ErrorMessage = "Los registros se insertaron correctamente"

    Session = sessionmaker(bind=engine)
    session = Session()
    log_list : List[HiredEmployees] = []
    exists_validation_error = False
    for hiredEmployee in listHiredEmployees:
        exists_validation_error = valitate_hired_employee(hiredEmployee)
        if not exists_validation_error:
            log_employee = HiredEmployees(
                id=hiredEmployee.id,
                name=hiredEmployee.name,
                datetime=hiredEmployee.dateTime,
                department_id=hiredEmployee.departmentId,
                job_id=hiredEmployee.jobId
            )
            log_list.append(log_employee)
            log_response = log_invalid_employee(log_list)
            response.Error = log_response.Error
            response.ErrorMessage = log_response.ErrorMessage
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
                response.ErrorMessage = "Registro insertado correctamente"
            except Exception as e:
                session.rollback()
                response.Error = True
                response.ErrorMessage = str(e)
            finally:
                session.close()
    return response
    







