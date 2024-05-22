from azure.storage.blob import BlobServiceClient

class AzureBlobLogger:
    """
    A class for logging data to Azure Blob Storage.
    
    Attributes:
        connection_string (str): The connection string for the Azure Blob Storage account.
        container_name (str): The name of the container in Azure Blob Storage.
        blob_service_client (BlobServiceClient): The BlobServiceClient instance for interacting with the Blob service.
        container_client (ContainerClient): The ContainerClient instance for interacting with the container.
    """
    
    def __init__(self, connection_string, container_name):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)


    def log_data(self, data, blob_name):
        """
        Uploads the provided data to Azure Blob Storage with the specified blob name.
        
        Args:
            data: The data to be uploaded.
            blob_name (str): The name of the blob.
        """
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.upload_blob(data, overwrite=True)