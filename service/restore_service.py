import datetime
from io import BytesIO
from sqlalchemy import create_engine
import pandas as pd
from azure.storage.blob import BlobServiceClient
from fastavro import reader
from models.response.base_response_model import BaseResponseModel

class RestoreService:
    """
    A class that provides methods to restore data from an Avro file in Azure Blob Storage to a SQL Server table.
    
    Args:
        connection_string (str): The connection string for the SQL Server.
        container_name (str): The name of the Azure Blob Storage container.
        blob_name (str): The name of the blob file to be restored.
    """
    def __init__(self, db_connection_string, dl_connection_string, container_name):
        self.db_connection_string = db_connection_string
        self.dl_connection_string = dl_connection_string
        self.container_name = container_name

    def restore_table_from_blob(self, table_name) -> BaseResponseModel:
        """
        Restores the data from an Avro file in Azure Blob Storage to the specified SQL Server table.
        
        Args:
            table_name (str): The name of the table where data will be restored.
        """
        response = BaseResponseModel()
        response.Error = False
        response.ErrorMessage = ""
        
        try:

            blob_service_client = BlobServiceClient.from_connection_string(self.dl_connection_string)
            container_client = blob_service_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(f'{table_name}.avro')
            stream = blob_client.download_blob().readall()
            

            avro_stream = BytesIO(stream)
            avro_stream.seek(0) 

            records = [record for record in reader(avro_stream)]
            df = pd.DataFrame(records)

            # Connect to SQL Server and insert data
            engine = create_engine(self.db_connection_string)
            with engine.begin() as conn:
                df.to_sql(table_name, con=conn, if_exists='replace', index=False)

        except Exception as e:
            response.Error = True
            response.ErrorMessage = str(e)

        return response
