import streamlit as st
import json
import os

from azure_batch_transcribe import transcribe
from file_processing import download_and_upload_file,create_service_sas_blob
from azure_openai import open_ai_chat


with open(r'config.json') as config_file:
    config_details = json.load(config_file)

STORAGE_ACCOUNT_SHARED_ACCESS_KEY = os.getenv("STORAGE_ACCOUNT_SHARED_ACCESS_KEY")

#STORAGE_ACCOUNT_SHARED_ACCESS_KEY = st.secrets["azure_storage"]["STORAGE_ACCOUNT_SHARED_ACCESS_KEY"]


if __name__ == "__main__":

    #video_url = 'https://www.youtube.com/watch?v=ry2_cFPewVM'
    
    st.header('Azure speech service', divider='rainbow')
    video_url = st.text_input('Youtube URL','paste link here')
    if video_url == 'paste link here':
        exit(0)
    else:
        blob_client,blob_file_name = download_and_upload_file(video_url)
        sas_token = create_service_sas_blob(blob_client,STORAGE_ACCOUNT_SHARED_ACCESS_KEY)
        sas_url = f"{blob_client.url}?{sas_token}"
        #print(sas_url)
        transcribe_op = transcribe(sas_url)
        print(transcribe_op)

    response_fn_test = open_ai_chat(['''sentence is  - ''' + '''"''' + transcribe_op + '''"'''+ '''.'''])
    print(response_fn_test)