import os
from dotenv import load_dotenv

def load_config():
    os.environ.clear()
    load_dotenv()
    return {
        "BASE_URL": os.getenv("BASE_URL"),
        "OKTA_ACCESS_TOKEN": os.getenv("OKTA_ACCESS_TOKEN"),
        "SUBSCRIPTION_KEY": os.getenv("SUBSCRIPTION_KEY"),
        "ADO_PAT": os.getenv("ADO_PAT"),
        "ADO_BASE_URL": os.getenv("ADO_BASE_URL")
    }