import streamlit as st
from pytube import YouTube
import os
import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, generate_blob_sas, BlobSasPermissions
from moviepy.editor import *
import json

with open(r'config.json') as config_file:
    config_details = json.load(config_file)

STORAGE_ACCOUNT_NAME = config_details['STORAGE_ACCOUNT_NAME']
CONTAINER_NAME = config_details['CONTAINER_NAME']
STORAGE_ACCOUNT_SHARED_ACCESS_KEY = os.getenv("STORAGE_ACCOUNT_SHARED_ACCESS_KEY")


def get_blob_service_client_account_key():
    # TODO: Replace <storage-account-name> with your actual storage account name
    account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
    shared_access_key = STORAGE_ACCOUNT_SHARED_ACCESS_KEY
    credential = shared_access_key

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient(account_url, credential=credential)

    return blob_service_client

def upload_blob_file(blob_service_client: BlobServiceClient, container_name: str, file_name: str):
    container_client = blob_service_client.get_container_client(container=container_name)
    with open(file=file_name, mode="rb") as data:
        blob_client = container_client.upload_blob(name=file_name, data=data, overwrite=True)

    return blob_client

def create_service_sas_blob(blob_client: BlobClient,account_key: str):
    # Create a SAS token that's valid for one day, as an example

    utc_now = datetime.datetime.now(datetime.timezone.utc)
    utc_later = utc_now + datetime.timedelta(minutes=20)

# Format the UTC time as a string
    start_time = utc_now.strftime('%Y-%m-%dT%H:%M:%SZ')
    expiry_time = utc_later.strftime('%Y-%m-%dT%H:%M:%SZ')

    print(start_time)
    print(expiry_time)

    sas_token = generate_blob_sas(
        account_name=blob_client.account_name,
        container_name=blob_client.container_name,
        blob_name=blob_client.blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        start=start_time,
        expiry=expiry_time
        
    )
    return sas_token



def download_and_upload_file(video_link):
    print("Reading data")
    video = YouTube(video_link)
    print("Extracting audio streams")
    data_stream = video.streams.filter(only_audio=True, file_extension='mp4').first()
    print("Downloading audio")
    data_stream.download()
    print("Audio downloaded")
    path = data_stream.default_filename
    mp3_file_name = path.replace(".mp4", ".mp3")
    audio_clip = AudioFileClip(path)
    audio_clip.write_audiofile(mp3_file_name, codec='libmp3lame')
    os.remove(path)
    blob_service_client = get_blob_service_client_account_key()
    print(mp3_file_name)
    blob_client = upload_blob_file(blob_service_client, CONTAINER_NAME, mp3_file_name)
    print("file uploaded!")
    os.remove(mp3_file_name)
    return blob_client,mp3_file_name