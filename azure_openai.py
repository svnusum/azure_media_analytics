
import openai
import json
import streamlit as st
import os

with open(r'config.json') as config_file:
    config_details = json.load(config_file)

# This is set to `azure`
OPEN_AI_API_TYPE = config_details['OPEN_AI_API_TYPE']
# The API key for your Azure OpenAI resource.
AZURE_OPEN_AI_API_KEY = os.getenv("AZURE_OPEN_AI_API_KEY")
# The base URL for your Azure OpenAI resource. e.g. "https://<your resource name>.openai.azure.com"
AZURE_OPEN_AI_API_BASE = os.getenv("AZURE_OPEN_AI_API_BASE")
# Currently Chat Completion API have the following versions available: 2023-03-15-preview
AZURE_OPEN_AI_API_VERSION = config_details['AZURE_OPEN_AI_API_VERSION']
#Deployment name of the model deployed in your azure account
AZURE_OPEN_AI_DEPLOYMENT_NAME = config_details['AZURE_OPEN_AI_DEPLOYMENT_NAME']



PROMPT = """
You will be acting as an agent who can fetch details from a given text input
Here are 4 critical rules for the interaction you must abide:
<rules>
1. For each stock being recommended You MUST fetch details like speaker_name,stock_name,stock symbol,stock buy or sell, target price, stop loss price
2. If any of the above detail is not present for any stock return 'NA' for that field
3. DO NOT put numerical at the very front of output.
4. You MUST return the output in csv format with all the collected details
</rules>
"""


def open_ai_chat(user_assistant):

    # This is set to `azure`
    openai.api_type = OPEN_AI_API_TYPE
    # The API key for your Azure OpenAI resource.
    openai.api_key = AZURE_OPEN_AI_API_KEY
    # The base URL for your Azure OpenAI resource. e.g. "https://<your resource name>.openai.azure.com"
    openai.api_base = AZURE_OPEN_AI_API_BASE
    # Currently Chat Completion API have the following versions available: 2023-03-15-preview
    openai.api_version = AZURE_OPEN_AI_API_VERSION
    
    assert isinstance(user_assistant, list), "`user_assistant` should be a list"
    system_msg = [{"role": "system", "content": PROMPT}]

    user_assistant_msgs = [
      {"role": "assistant", "content": user_assistant[i]} if i % 2 else {"role": "user", "content": user_assistant[i]}
      for i in range(len(user_assistant))]

    msgs = system_msg + user_assistant_msgs

    try:
        response = openai.ChatCompletion.create(
                  engine=AZURE_OPEN_AI_DEPLOYMENT_NAME,
                  messages=msgs,
                  temperature=0,  # Control the randomness of the generated response
                  n=1,  # Generate a single response
                  stop=None
                )
    

        return response['choices'][0]['message']['content']
    
    except openai.OpenAIError as e:
        # Handle API error here, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")