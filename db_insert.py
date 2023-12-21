import os
from azure.cosmos import CosmosClient

from dotenv import load_dotenv

load_dotenv()

COSMOS_DB_ENDPOINT = os.getenv("COSMOS_DB_ENDPOINT")
COSMOS_DB_AUTH_KEY = os.getenv("COSMOS_DB_AUTH_KEY")

def cosmos_db_insert(cosmos_items):

    client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_AUTH_KEY)
    database = client.get_database_client('mediaAnalyticsDb')
    container = database.get_container_client('mediaItemStore')
    for item in cosmos_items:
        item['id'] = item['speaker_name']
        item['part_key'] = f"{item['speaker_name']}|{item['stock_name']}"
        container.create_item(body=item)