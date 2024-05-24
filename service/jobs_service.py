from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import datetime
import re
from logger.logger import AzureBlobLogger
from models.entities.log_jobs import LogJobs
from models.request.jobs_request_model import JobRequestModel
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

class Jobs(Base):
    """
    Represents a job.

    Attributes:
        id (int): The unique identifier for the job.
        job (str): The name of the job.
    """
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, autoincrement=False)
    job = Column(String, nullable=False)



def valitate_jobs(job: JobRequestModel) -> bool:
    """
    Validates the job data.

    Args:
        job (JobsRequestModel): The hired employee object to be validated.

    Returns:
        bool: False if the hired employee data is valid, True otherwise.
    """
    if job.id is None:
        return True, "El campo id es requerido"
    if job.job is None:
        return True, "El campo job es requerido"
    
    if not re.match(r'^[a-zA-Z0-9 ]+$', job.job):
        return True, "El campo job solo puede contener letras y numeros"
    if not re.match(r'^[0-9 ]+$', job.id):
        return True, "El campo id solo puede contener numeros"
    
    return False, ""


def log_invalid_jobs(listLogJobs: List[LogJobs]) -> BaseResponseModel:
    """
    Logs the list of jobs to an Azure Blob Storage container.

    Args:
        listLogJobs (List[LogJobs]): A list of jobs.

    Returns:
        BaseResponseModel: The response model indicating the success or failure of the logging operation.
    """
    response = BaseResponseModel()
    response.Error = False
    response.ErrorMessage = ""
    try:
        azure_blob_logger = AzureBlobLogger(dl_connection, container_name)
        timestamp = datetime.datetime.now().isoformat()
        log_blob_name = f'jobs_{timestamp}.log'
        jobs_json = '[' + ','.join([job.model_dump_json() for job in listLogJobs]) + ']'
        azure_blob_logger.log_data(jobs_json, log_blob_name)
        response.Error = True
        response.ErrorMessage = "El proceso detecto registros invalidos, se genero un log con los registros."
    except Exception as e:
        response.Error = True
        response.ErrorMessage = str(e)
    return response


def insert_jobs(listLogJobs: List[JobRequestModel]) -> BaseResponseModel:
    """
    Inserts a list of jobss into the database.

    Args:
        listLogJobs (List[JobsRequestModel]): A list of JobsRequestModel objects representing the jobs to be inserted.

    Returns:
        BaseResponseModel: A BaseResponseModel object indicating the success or failure of the operation.

    """
    response = BaseResponseModel()
    
    Session = sessionmaker(bind=engine)
    session = Session()
    log_list : List[LogJobs] = []
    exists_validation_error = False
    enable_log = False
    for job in listLogJobs:
        exists_validation_error, error_validation_message = valitate_jobs(job)
        if exists_validation_error:
            log_list = add_job_to_log(log_list, job, error_validation_message)
            enable_log = True
        else:
            new_job = Jobs(
                id=job.id,
                job=job.job,
            )

            try:
                session.add(new_job)
                session.commit()
                response.Error = False
                response.ErrorMessage = "Los registros se insertaron correctamente"
            except IntegrityError as e: 
                session.rollback()
                result = set_specific_error_message(str(e.orig))
                log_list = add_job_to_log(log_list, job, result.ErrorMessage)
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
        log_response = log_invalid_jobs(log_list)
        response.Error = log_response.Error
        response.ErrorMessage = log_response.ErrorMessage
    return response
    
def add_job_to_log(log_list: List[LogJobs], job: JobRequestModel, error_validation_message: str) -> List[LogJobs]:
    log_job = LogJobs()
    log_job.id=job.id
    log_job.job=job.job
    log_job.error_message=error_validation_message
    log_list.append(log_job)
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







