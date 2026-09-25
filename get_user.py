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

login = input("Enter the user's login (usually their email): ")

url = f"{ORG}/api/v1/users/{login}"
response = requests.get(url, headers=headers)
user = response.json()
user_id = user['id']
first_name = user['profile']['firstName']
last_name = user['profile']['lastName']

print(f"Name: {first_name} {last_name}\n"
      f"ID: {user_id}")