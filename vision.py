import os
import requests
import base64

# Configuration
GPT4V_KEY = ""
IMAGE_PATH = r"C:\Users\suryavalluri\Desktop\media-analytics-new\nseit-media-analytics\Expert Stock Picks Kunal Bothra & Nooresh Meranis Top Buy Recommendations With Target & Stop Loss.mp4_frames\frame11.jpg"
encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')
headers = {
    "Content-Type": "application/json",
    "api-key": GPT4V_KEY,
}

# Payload for the request
payload = {
  "dataSources": [
    {
      "type": "AzureCognitiveSearch",
      "parameters": {
        "endpoint": "https://nseit-ai-search.search.windows.net",
        "key": ""
      }
    }
  ],
  "enhancements": {
    "ocr": {
      "enabled": True
    },
    "grounding": {
      "enabled": True
    }
  },
  "messages": [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are an AI assistant that summarizes video, paying attention to important events, people, and objects in the video."
        }
      ]
    }
  ],
  "temperature": 0,
  "top_p": 1,
  "max_tokens": 800
}

GPT4V_ENDPOINT = ""

# Send request
try:
    response = requests.post(GPT4V_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
except requests.RequestException as e:
    raise SystemExit(f"Failed to make the request. Error: {e}")

# Handle the response as needed (e.g., print or process)
print(response.json())