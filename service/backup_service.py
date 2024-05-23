import datetime
from sqlalchemy import create_engine, MetaData, Table
import pandas as pd
from azure.storage.blob import BlobServiceClient
from fastavro import writer,  parse_schema
from models.response.base_response_model import BaseResponseModel

class BackupService:
    """
    A class that provides methods to backup data from a SQL Server table to Azure Blob Storage.
    
    Args:
        connection_string (str): The connection string for the SQL Server.
        container_name (str): The name of the Azure Blob Storage container.
        blob_name (str): The name of the blob file to be created.
    """
    def __init__(self, db_connection_string, dl_connection_string, container_name):
        self.db_connection_string = db_connection_string
        self.dl_connection_string = dl_connection_string
        self.container_name = container_name

    def backup_table_to_blob(self, table_name) -> BaseResponseModel:
        """
        Backs up the data from the specified SQL Server table to an Avro file and uploads it to Azure Blob Storage.
        
        Args:
            table_name (str): The name of the table to backup.
        """
        response = BaseResponseModel()
        response.Error = False
        response.ErrorMessage = ""
       
        try:
            engine = create_engine(self.db_connection_string)
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=engine)
            schema = {
            "type": "record",
            "name": table_name,
            "fields": []
            }

            for column in table.columns:
                avro_type = None
                if column.type.python_type is int:
                    avro_type = 'int'
                elif column.type.python_type is float:
                    avro_type = 'float'
                elif column.type.python_type is bool:
                    avro_type = 'boolean'
                elif column.type.python_type is str:
                    avro_type = 'string'
                elif column.type.python_type in [datetime.date, datetime.datetime]:
                    avro_type = 'string'  # Usar 'string' para representar fechas y horas en Avro
                else:
                    avro_type = 'string'  # Asigna un tipo por defecto o maneja otros tipos específicamente

                field = {
                    "name": column.name,
                    "type": ["null", avro_type],  # Acepta nulos
                    "default": None  
                }
                schema["fields"].append(field)

            
            with engine.connect() as conn:
                df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
                df = convert_datetime_to_string(df) 

                parsed_schema = parse_schema(schema)
                with open(f'{table_name}.avro', 'wb') as out:
                    records = df.to_dict('records')  
                    writer(out, parsed_schema, records)


                blob_service_client = BlobServiceClient.from_connection_string(self.dl_connection_string)
                container_client = blob_service_client.get_container_client(self.container_name)
                blob_client = container_client.get_blob_client(f'{table_name}.avro')
                with open(f'{table_name}.avro', "rb") as avro_file:
                    blob_client.upload_blob(avro_file, overwrite=True)
        except Exception as e:
            response.Error = True
            response.ErrorMessage = str(e)

        return response
    

def convert_datetime_to_string(df):
    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            df[column] = df[column].apply(lambda x: x.isoformat() if pd.notnull(x) else None)
    return df