import requests
import json
import logging
from .config import load_config

config = load_config()

def get_embeddings(sentences):
    url = f"{config['BASE_URL']}/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['OKTA_ACCESS_TOKEN']}",
        "Subscription-Key": config['SUBSCRIPTION_KEY']
    }
    payload = {
        "inputs": sentences,
        "requestOptions": {
            "model": "TEXT_EMBEDDING_ADA_002"
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
        data = response.json()
        logging.debug(f"API Response Type: {type(data)}")
        logging.debug(f"API Response Content: {json.dumps(data, indent=2)}")
        
        if data.get('success') and 'data' in data and 'embeddings' in data['data']:
            return data['data']['embeddings']
        else:
            logging.error(f"Unexpected response structure: {data}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in API request: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        logging.error(f"Raw response: {response.text}")
        return None

class Embeddings:
    def embed_documents(self, texts):
        embeddings = get_embeddings(texts)
        if embeddings is None or not embeddings:
            raise ValueError("Failed to get embeddings")
        return embeddings

    def embed_query(self, text):
        result = get_embeddings([text])
        if result is None or not result:
            raise ValueError("Failed to get query embedding")
        return result[0]
