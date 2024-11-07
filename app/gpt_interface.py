import requests
import json
import logging
from .config import load_config

config = load_config()

def ask_gpt(query: str):
    url = f"{config['BASE_URL']}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['OKTA_ACCESS_TOKEN']}",
        "Subscription-Key": config['SUBSCRIPTION_KEY']
    }
    payload = {
        "model": "GPT_4_O",
        "messages": [
            {"role": "user", "content": query}
        ],
         "max_tokens": 2000
    }

    logging.debug(f"Sending request to: {url}")
    logging.debug(f"Headers: {json.dumps(headers, indent=2)}")
    logging.debug(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        logging.debug(f"Response status code: {response.status_code}")
        logging.debug(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
        logging.debug(f"Response content: {response.text}")
        
        if response.status_code == 500:
            logging.error("Received 500 error from server. This might be a server-side issue.")
            return None

        response.raise_for_status()
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content']
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
    
def transform_question(query: str):
    prompt = f"""
    Based on the following user question, please provide:
    1. A concise title for a support ticket (max 100 characters)
    2. A detailed description of the issue and any relevant context
    3. A suggested priority level (1-4, where 1 is highest and 4 is lowest)

    User question: {query}

    Format your response as follows:
    Title: [Your suggested title]
    Description: [Your detailed description]
    Priority: [Suggested priority number]

    """
    
    response = ask_gpt(prompt)
    
    if response:
        # Parse the response
        lines = response.split('\n')
        title = lines[0].replace('Title: ', '').strip()
        description = '\n'.join(lines[1:-1]).replace('Description: ', '').strip()
        priority = int(lines[-1].replace('Priority: ', '').strip())
        
        return {
            "title": title,
            "description": description,
            "priority": priority
        }
    else:
        return None