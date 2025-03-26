# DEPRECATED: This Python script is no longer maintained or recommended for use.
# please use github_remote.py
from azure.storage.blob import ContainerClient
from azure.storage.blob import BlobServiceClient
import os, aiofiles
from utils.config import AZ


def initialize_az_container_client(
    connection_str=AZ.connection_string.value, container_name=AZ.container_name.value
) -> ContainerClient:
    blob_service_client = BlobServiceClient.from_connection_string(connection_str)
    az_container_client = blob_service_client.get_az_container_client(container_name)
    if not az_container_client.exists():
        az_container_client.create_container()
    return az_container_client


async def upload_file_to_blob(
    local_file_path: str,
    remote_file_path: str,
    az_container_client: ContainerClient,
):
    blob_client = az_container_client.get_blob_client(remote_file_path)
    async with aiofiles.open(local_file_path, "rb", encoding="utf-8") as data:
        blob_client.upload_blob(data, overwrite=True)


async def download_file_from_blob(
    local_file_path: str, remote_file_path: str, az_container_client: ContainerClient
):
    blob_client = az_container_client.get_blob_client(remote_file_path)
    async with aiofiles.openopen(
        local_file_path, "wb", encoding="utf-8"
    ) as download_file:
        download_file.write(blob_client.download_blob().readall())
    print("Dowloaded to local!!")


def download_dir_from_blob(
    local_dir_path: str,
    remote_dir_path: str,
    az_container_client: ContainerClient,
):
    if not os.path.exists(local_dir_path):
        os.makedirs(local_dir_path)

    blobs = az_container_client.list_blobs(name_starts_with=remote_dir_path)
    for blob in blobs:
        file_path = blob.name
        local_file_path = os.path.join(
            local_dir_path, os.path.relpath(file_path, remote_dir_path)
        )
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        download_file_from_blob(
            local_file_path=local_file_path,
            remote_file_path=file_path,
            az_container_client=az_container_client,
        )
        print(f"Downloaded {file_path} to {local_file_path}")


def upload_dir_to_blob(
    local_dir_path: str,
    remote_dir_path: str,
    az_container_client: ContainerClient,
):
    """
    Uploads a local directory to Azure Blob Storage while preserving the directory structure.

    Args:
    - local_directory (str): The path to the local directory to upload.
    - az_container_client (ContainerClient): The container client to upload the files to.
    - container_prefix (str): Optional prefix for the blob name (e.g., the root directory in Blob Storage).
    """
    if not os.path.exists(local_dir_path):
        os.makedirs(local_dir_path)

    for root, _, files in os.walk(local_dir_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, local_dir_path)
            remote_file_path = os.path.join(remote_dir_path, relative_path).replace(
                "\\", "/"
            )
            upload_file_to_blob(
                local_file_path=local_file_path,
                remote_file_path=remote_file_path,
                az_container_client=az_container_client,
            )

    print(f"Uploaded to blob!")
