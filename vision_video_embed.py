import requests
import json

OCP_APIM_SUBSCRIPTION_KEY = ''
API_VERSION = '2023-05-01-preview'
VISION_END_POINT = 'nseit-ai-msa-westus.cognitiveservices.azure.com'

def createindex():

    headers = {
        'Ocp-Apim-Subscription-Key': OCP_APIM_SUBSCRIPTION_KEY,
        'Content-Type': 'application/json',
    }

    params = {
        'api-version': API_VERSION,
    }

    data = "\n{\n  'metadataSchema': {\n    'fields': [\n      {\n        'name': 'cameraId',\n        'searchable': false,\n        'filterable': true,\n        'type': 'string'\n      },\n      {\n        'name': 'timestamp',\n        'searchable': false,\n        'filterable': true,\n        'type': 'datetime'\n      }\n    ]\n  },\n  'features': [\n    {\n      'name': 'vision',\n      'domain': 'surveillance'\n    },\n    {\n      'name': 'speech'\n    }\n  ]\n}"

    response = requests.put(
        'https://nseit-ai-msa-westus.cognitiveservices.azure.com/computervision/retrieval/indexes/my-video-index',
        params=params,
        headers=headers,
        data=data,
    )

    return response


def add_videos():

    headers = {
    'Ocp-Apim-Subscription-Key': OCP_APIM_SUBSCRIPTION_KEY,
    'Content-Type': 'application/json',
    }

    params = {
        'api-version': API_VERSION,
    }

    data = "\n{\n  'videos': [\n    {\n      'mode': 'add',\n      'documentId': '02a504c9cd28296a8b74394ed7488049',\n      'documentUrl': 'https://mediafileswestus.blob.core.windows.net/video-files/Expert%20Stock%20Picks%20Kunal%20Bothra%20%26%20Nooresh%20Meranis%20Top%20Buy%20Recommendations%20With%20Target%20%26%20Stop%20Loss.mp4?sp=racwdymeop&st=2024-01-17T05:23:48Z&se=2024-01-17T13:23:48Z&spr=https&sv=2022-11-02&sr=b&sig=BqFU50RglNcyPzQ5p1dyfwdNLv2CGtGrhpbC7O5yoiM%3D',\n      'metadata': {\n        'cameraId': 'camera3',\n        'timestamp': '2024-01-17 17:40:33'\n      }\n    }\n  ]\n}"

    response = requests.put(
        'https://nseit-ai-msa-westus.cognitiveservices.azure.com/computervision/retrieval/indexes/my-video-index/ingestions/my-ingestion-3',
        params=params,
        headers=headers,
        data=data,
    )

    return response


def vid_ingestion_status():
    headers = {
    'ocp-apim-subscription-key': OCP_APIM_SUBSCRIPTION_KEY,
    }

    params = {
        'api-version': API_VERSION,
        'top': '20'
    }

    response = requests.get(
        'https://nseit-ai-msa-westus.cognitiveservices.azure.com/computervision/retrieval/indexes/my-video-index/ingestions',
        params=params,
        headers=headers,
    )

    return response

def get_video_summary():

    headers = {
    'Content-Type': 'application/json',
    'api-key': ''
    }

    body = {
    "enhancements": {
            "video": {
              "enabled": 'true'
            }
    },
    "dataSources": [
    {
        "type": "AzureComputerVisionVideoIndex",
        "parameters": {
            "computerVisionBaseUrl": "https://nseit-ai-msa-westus.cognitiveservices.azure.com/",
            "computerVisionApiKey": "",
            "indexName": "my-video-index",
            "videoUrls": ["https://mediafileswestus.blob.core.windows.net/video-files/Expert%20Stock%20Picks%20Kunal%20Bothra%20%26%20Nooresh%20Meranis%20Top%20Buy%20Recommendations%20With%20Target%20%26%20Stop%20Loss.mp4?sp=racwdymeop&st=2024-01-17T05:23:48Z&se=2024-01-17T13:23:48Z&spr=https&sv=2022-11-02&sr=b&sig=BqFU50RglNcyPzQ5p1dyfwdNLv2CGtGrhpbC7O5yoiM%3D"]
        }
    }],
    "messages": [ 
        {
            "role": "system", 
            "content": "You are a helpful assistant." 
        },
        {
            "role": "user",
            "content": [
                    {
                        "type": "text",
                        "text": "summarize the video:"
                    }
                ]
        },
        {
            "role": "user",
            "content": [
                    {
                        "type": "acv_document_id",
                        "acv_document_id": "02a504c9cd28296a8b74394ed7488049"
                    }
                ]
        }
    ],
    "max_tokens": 1000, 
            }


    response = requests.post(
        'https://nseit-gpt4-vision.openai.azure.com/openai/deployments/gpt4-vision/extensions/chat/completions?api-version=2023-12-01-preview',
        data=json.dumps(body),
        headers=headers
    )

    return response



if __name__ == "__main__":

    #create_index_resp = createindex()
    #print(create_index_resp.content)

    #vid_add_resp = add_videos()
    #print(vid_add_resp.content)

    #ing_status_resp = vid_ingestion_status()
    #print(ing_status_resp.content)

    summ_resp = get_video_summary()
    print(summ_resp.content)