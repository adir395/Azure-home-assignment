from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

STORAGE_ACCOUNT_A_CONNECTION_STRING = os.getenv("STORAGE_ACCOUNT_A_CONNECTION_STRING")
STORAGE_ACCOUNT_B_CONNECTION_STRING = os.getenv("STORAGE_ACCOUNT_B_CONNECTION_STRING")
CONTAINER_NAME_A = os.getenv("CONTAINER_NAME_A")
CONTAINER_NAME_B = os.getenv("CONTAINER_NAME_B")
ACCOUNT_KEY_A = os.getenv("ACCOUNT_KEY_A")


def test_connection(blob_service_client, account_name):
    try:
        blob_service_client.get_account_information()
        print(f"Connection to account '{account_name}' successful!")
    except Exception as e:
        print(f"Connection to account '{account_name}' failed: {e}")
        raise


def create_container_if_not_exists(container_client):
    try:
        container_client.create_container()
        print(f"Container '{container_client.container_name}' created successfully.")
    except Exception as e:
        if "ContainerAlreadyExists" in str(e):
            print(f"Container '{container_client.container_name}' already exists.")
        else:
            print(f"Error creating container '{container_client.container_name}': {e}")


def generate_sas_token(account_name, container_name, blob_name, account_key):
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
    )
    return sas_token


def create_and_upload_blobs():
    blob_service_client_a = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_A_CONNECTION_STRING)
    container_client_a = blob_service_client_a.get_container_client(CONTAINER_NAME_A)

    test_connection(blob_service_client_a, "Account A")
    create_container_if_not_exists(container_client_a)

    for i in range(1, 101):
        blob_name = f"blob-{i}.txt"
        blob_client = container_client_a.get_blob_client(blob_name)
        blob_content = f"This is the content of blob {i}"
        try:
            blob_client.upload_blob(blob_content, overwrite=True)
            print(f"Uploaded {blob_name} to Storage Account A")
        except Exception as e:
            print(f"Failed to upload {blob_name}: {e}")


def copy_blobs_to_storage_b():
    blob_service_client_a = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_A_CONNECTION_STRING)
    blob_service_client_b = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_B_CONNECTION_STRING)

    container_client_a = blob_service_client_a.get_container_client(CONTAINER_NAME_A)
    container_client_b = blob_service_client_b.get_container_client(CONTAINER_NAME_B)

    test_connection(blob_service_client_b, "Account B")
    create_container_if_not_exists(container_client_b)

    blobs_list = container_client_a.list_blobs()
    for blob in blobs_list:
        try:
            # Generate SAS token for source blob
            sas_token = generate_sas_token(
                account_name=blob_service_client_a.account_name,
                container_name=CONTAINER_NAME_A,
                blob_name=blob.name,
                account_key=ACCOUNT_KEY_A
            )
            source_blob_url = f"https://{blob_service_client_a.account_name}.blob.core.windows.net/{CONTAINER_NAME_A}/{blob.name}?{sas_token}"

            # Copy blob to Storage Account B
            blob_client_b = container_client_b.get_blob_client(blob.name)
            blob_client_b.start_copy_from_url(source_blob_url)
            print(f"Copied {blob.name} from Storage Account A to B")
        except Exception as e:
            print(f"Failed to copy {blob.name}: {e}")


if __name__ == "__main__":
    create_and_upload_blobs()
    copy_blobs_to_storage_b()
