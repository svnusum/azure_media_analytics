import streamlit as st
from pytube import YouTube
import os
from datetime import datetime,timezone,timedelta
from azure.storage.blob import BlobServiceClient, BlobClient, generate_blob_sas, BlobSasPermissions
from moviepy.editor import *
import json
import pandas as pd
import easyocr
import cv2
import shutil
import re
from dotenv import load_dotenv

load_dotenv()

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

    utc_now = datetime.now(timezone.utc)
    utc_later = utc_now + timedelta(minutes=20)

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


def video_download(video_link):

    print("downloading video")
    video = YouTube(video_link)
    data_stream = video.streams.filter(progressive=True,file_extension = "mp4").first()
    data_stream.download()
    video_file_name = data_stream.default_filename

    #video_file_name = video_file_name.replace("´","")

    return video_file_name

def extract_video_frames(video_file_name):

    current_directory = os.getcwd()
    #pro_video_file_name = re.escape(video_file_name)
    frames_directory = os.path.join(current_directory, f'{video_file_name}_frames')
    if os.path.exists(frames_directory) and os.path.isdir(frames_directory):
        shutil.rmtree(frames_directory)
    if not os.path.exists(frames_directory):
        os.makedirs(frames_directory)
    print("extracting frames from video")
    vidcap = cv2.VideoCapture(video_file_name)
    fps = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(fps)
    output = pd.DataFrame()
    count = 0
    success = True
    assert vidcap.isOpened()
    while success:
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*3000))
        success,image = vidcap.read()
        if not success: break
        frame_time = str(datetime.now()).split()[1]
        cv2.imwrite(os.path.join(frames_directory,'frame%d.jpg'%count),image)
        dict_1 = {'file_name':'frame%d.jpg'%count, 'frame_time':frame_time}
        output = pd.concat([output, pd.DataFrame([dict_1])], ignore_index=True)
        count = count + 1    
    vidcap.release()
    os.remove(video_file_name)
    print('Successfully Completed')
    print(output)
    return output,frames_directory

def extract_text_from_frames(output,frames_directory):

    frame_texts=[]
    for filename in output['file_name'].to_list():
        #print(filename)
        reader = easyocr.Reader(['en'])
        #reader = easyocr.Reader(['en'],download_enabled=False ,model_storage_directory="./.EasyOCR/model")
        result = reader.readtext(os.path.join(frames_directory,filename))
        text = ' '
        for i in result:
            text += i[1] + " "
        frame_texts.append(text)

    if os.path.exists(frames_directory) and os.path.isdir(frames_directory):
        shutil.rmtree(frames_directory)

    return frame_texts

if __name__ == "__main__":

    #video_link = 'https://www.youtube.com/watch?v=ry2_cFPewVM'
    video_link = 'https://www.youtube.com/watch?v=YsT-84HEysI&t=71s'
    video_file_name = video_download(video_link)
    output,frames_directory = extract_video_frames(video_file_name)
    frame_texts = extract_text_from_frames(output,frames_directory)
    print(frame_texts)
