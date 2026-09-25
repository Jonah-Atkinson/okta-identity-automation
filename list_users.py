import os
import requests
from dotenv import load_dotenv


load_dotenv()

ORG = os.environ["OKTA_ORG_URL"]
TOKEN = os.environ["OKTA_API_TOKEN"]

headers = {
    "Authorization": f"SSWS {TOKEN}",
    "Accept": "application/json",
    "rel": "next"
}

url = f"{ORG}/api/v1/users/"
response = requests.get(url, headers=headers)
users = response.json()
for user  in users:
    user_id = user["id"]
    first_name = user['profile']['firstName']
    last_name = user['profile']['lastName']
    primary_email = user['profile']['email']
    print(f"Name:{first_name} {last_name}\nID:{user_id}\nPrimary Email:{primary_email}\n")