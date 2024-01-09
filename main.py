import streamlit as st
import json
import os
import pandas as pd

from azure_batch_transcribe import transcribe
from file_processing import download_and_upload_file,create_service_sas_blob,video_download,extract_video_frames,extract_text_from_frames
from azure_openai import open_ai_chat
from db_insert import cosmos_db_insert

from dotenv import load_dotenv

load_dotenv()


with open(r'config.json') as config_file:
    config_details = json.load(config_file)

STORAGE_ACCOUNT_SHARED_ACCESS_KEY = os.getenv("STORAGE_ACCOUNT_SHARED_ACCESS_KEY")




#STORAGE_ACCOUNT_SHARED_ACCESS_KEY = st.secrets["azure_storage"]["STORAGE_ACCOUNT_SHARED_ACCESS_KEY"]


prompt_1 = """
create a transcription summary with respect to stock recommendations in shared transcript.
only include the stock,stock_symbol, buy or sell recommendations also identify who suggested it,stop loss and target price.
out of values provided in the input the lower value will be the stop loss and the higher value will be target price.
The stop loss price MUST ALWAYS BE lower than target price so pick the values accordingly.
strictly generate details for a stock only once, DO NOT generate duplicates.
Return a single line for each stock. If there are not stocks recommended just return - 'No stocks recommended'

"""


prompt_2= """
You will be acting as an agent who can fetch details from a given text input

Here are 7 critical rules for the interaction you must abide:
<rules>
1. For each stock being recommended You MUST fetch details like speaker_name,stock_name,stock symbol,stock buy or sell, target price, stop loss price
2. Please identify Indian names as well
3. If any of the above detail is not present for any stock return 'NA' for that field
4. DO NOT put numerical at the very front of output.
5. You MUST return the output in csv format with all the collected details
6. If a range is mentioned for price then pick the higher value
7. Strictly do not use commas while representing numbers

</rules>

"""

prompt_3 = """ 

you will be acting as an information retreiver from two given inputs, one is a audio transcription and another is video transcription.

Here are the critical rules for the interaction you must abide:

<rules>
1.) using the audio and video transcription, for each stock being recommended You MUST fetch details like 
    speaker_name,stock_name,stock symbol,stock buy or sell, target price, stop loss price.
2.) cross check person names and stock names between audio and video transcription. 
3.) do not mention audio/video in output
4.) If any of the above detail is not present for any stock return 'NA' for that field
5.) DO NOT put numerical at the very front of output.
6.) You MUST return the output in csv format with all the collected details
7.) If a range is mentioned for price then pick the higher value
8.) Strictly do not use commas while representing numbers

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
        with st.expander("Video Transcription"):
            st.write(transcribe_op)
        #print(transcribe_op)
        #st.write(transcribe_op)

        with st.spinner('Generating video transcription summary...'):
            prompt_1_resp = open_ai_chat(prompt_1, ['''sentence is  - ''' + '''"''' + transcribe_op + '''"''' + '''.'''])
        with st.expander("Video transcription summary"):
            st.write(prompt_1_resp)
        
        with st.spinner('Extracting data from video transcription summary...'):
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
        with st.expander("Extracted data from video transcription summary"):
            st.dataframe(df)

        with st.spinner('Downloading video...'):
            video_file_name = video_download(video_url)
        with st.spinner('Generating frames from video...'):
            output,frames_directory = extract_video_frames(video_file_name)
        with st.spinner('Extracting text from video frames...'):
            frame_texts = extract_text_from_frames(output,frames_directory)
        with st.expander("Text from video"):
            st.write(str(frame_texts))
        
        with st.spinner('Generating summary from text in video...'):
            prompt_1_resp_txt = open_ai_chat(prompt_1, ['''Input is  - ''' + '''"''' + str(frame_texts) + '''"''' + '''.'''])
        with st.expander("Video text summary"):
            st.write(prompt_1_resp_txt)

        with st.spinner('Generating output based on audio and video text summary...'):
            prompt_3_resp = open_ai_chat(prompt_3, ['''video transcription - ''' + '''"''' + prompt_1_resp_txt + '''"''' + '''. \n \n '''\
                                                    + '''audio transcription - ''' + '''"''' + prompt_1_resp + '''"''' + '''.''' ])
        #with st.expander("collated audio & video data"):
        #    st.write(prompt_3_resp)

        result_array_2 = prompt_3_resp.split("\n")
        cols = result_array_2[0].split(',')
        rslt_rows = [r.split(',') for r in result_array_2[1::]]
        rslts_items = [
            dict(zip(cols, item))
            for item in rslt_rows
        ]
        #print(json.dumps(results_items, indent=4))
        df2 = pd.json_normalize(rslts_items)
        with st.expander("Extracted data from audio & video text summary"):
            st.dataframe(df2)
        #cosmos_db_insert(results_items)

        #txt = st.text_area(
        #                    "Ask questions related to the transcription below",
        #                    "",
        #                    )
        #if txt == '':
        #    exit(0)
        #else:
        #    own_prompt = '''You are a question answering bot. Answer the questions asked by the user about the provided text input. 
        #                    STRICTLY ANSWER OR RESPOND to questions only related to provided text input.
        #                    reply with 'I Cannot help with that request' if anything is asked outside the provided input'''
        #    own_prompt_response = open_ai_chat(own_prompt, ['''Text input is  - ''' + '''"''' + transcribe_op + '''"''' + '''.'''])