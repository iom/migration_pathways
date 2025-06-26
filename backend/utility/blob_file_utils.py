import json
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
import os
from dotenv import load_dotenv

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_CONTAINER = os.getenv("AZURE_BLOB_KB") 

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(BLOB_CONTAINER)

def read_json_from_blob(blob_name: str):
    try:
        blob_client = container_client.get_blob_client(blob_name)
        blob_data = blob_client.download_blob().readall()
        return json.loads(blob_data)
    except ResourceNotFoundError:
        print(f"Blob not found: {blob_name}")
        return []
    except Exception as e:
        print(f"Failed to read {blob_name} from blob: {e}")
        return []

def write_json_to_blob(blob_name: str, data):
    try:
        blob_client = container_client.get_blob_client(blob_name)
        json_data = json.dumps(data, indent=2)
        blob_client.upload_blob(json_data, overwrite=True)
        print(f" Successfully wrote {blob_name} to blob")
    except Exception as e:
        print(f" Failed to write {blob_name} to blob: {e}")
