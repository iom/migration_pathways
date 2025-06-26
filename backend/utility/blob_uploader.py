from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import os
from dotenv import load_dotenv

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_BLOB_UPLOAD", "uploaded-docs")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

def upload_to_azure_blob(file_stream, blob_name: str) -> str:
    try:
        print(f"Connecting to Azure Blob Storage...")

        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
        try:
            container_client.create_container()
            print(f"Created container: {AZURE_CONTAINER_NAME}")
        except ResourceExistsError:
            print(f"Container '{AZURE_CONTAINER_NAME}' already exists")

        print(f"Uploading file: {blob_name}")
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(file_stream, overwrite=True)

        blob_url = blob_client.url
        print(f"File uploaded to Azure Blob Storage at: {blob_url}")
        return blob_url

    except Exception as e:
        print(f"Azure Blob upload failed: {e}")
        raise
