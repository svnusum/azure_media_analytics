import streamlit as st
import json
import os
import pandas as pd

from azure_batch_transcribe import transcribe
from file_processing import download_and_upload_file,create_service_sas_blob
from azure_openai import open_ai_chat
from db_insert import cosmos_db_insert


with open(r'config.json') as config_file:
    config_details = json.load(config_file)

STORAGE_ACCOUNT_SHARED_ACCESS_KEY = os.getenv("STORAGE_ACCOUNT_SHARED_ACCESS_KEY")

#STORAGE_ACCOUNT_SHARED_ACCESS_KEY = st.secrets["azure_storage"]["STORAGE_ACCOUNT_SHARED_ACCESS_KEY"]


prompt_1 = """
create a transcription summary with respect to stock recommendations in shared transcript.
only include the stocks,stock_symbol, buy or sell recommendations also identify who suggested it,stop loss and target price.
Return a single line for each stock.

"""


prompt_2= """
You will be acting as an agent who can fetch details from a given text input

Here are 4 critical rules for the interaction you must abide:
<rules>
1. For each stock being recommended You MUST fetch details like speaker_name,stock_name,stock symbol,stock buy or sell, target price, stop loss price
2. If any of the above detail is not present for any stock return 'NA' for that field
3. DO NOT put numerical at the very front of output.
4. You MUST return the output in csv format with all the collected details
5. If a range is mentioned for price then pick the higher value

</rules>

"""


if __name__ == "__main__":

    #video_url = 'https://www.youtube.com/watch?v=ry2_cFPewVM'
    
    st.header('Market Guardian', divider='rainbow')
    video_url = st.text_input('Youtube URL','paste link here')
    if video_url == 'paste link here' or video_url == '':
        exit(0)
    else:
        st.video(video_url)
        with st.spinner('processing the video file...'):
            blob_client,blob_file_name = download_and_upload_file(video_url)
            sas_token = create_service_sas_blob(blob_client,STORAGE_ACCOUNT_SHARED_ACCESS_KEY)
            sas_url = f"{blob_client.url}?{sas_token}"
        #print(sas_url)
        with st.spinner('Transcribing video file...'):
            transcribe_op = transcribe(sas_url)
        #print(transcribe_op)
        #st.write(transcribe_op)

        prompt_1_resp = open_ai_chat(prompt_1, ['''sentence is  - ''' + '''"''' + transcribe_op + '''"''' + '''.'''])
        with st.expander("Transcription summary"):
            st.write(prompt_1_resp)
        response_fn_test = open_ai_chat(prompt_2, ['''sentence is  - ''' + '''"''' + prompt_1_resp + '''"''' + '''.'''])
    
        result_array = response_fn_test.split("\n")
        columns = result_array[0].split(',')
        result_rows = [r.split(',') for r in result_array[1::]]
        results_items = [
            dict(zip(columns, item))
            for item in result_rows
        ]
        #print(json.dumps(results_items, indent=4))
        df = pd.json_normalize(results_items)
        st.dataframe(df)

        cosmos_db_insert(results_items)