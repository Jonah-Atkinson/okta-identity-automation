import os
from dotenv import load_dotenv
from manage import manage_data


load_dotenv()

ORG = os.environ["OKTA_ORG_URL"]

url = f"{ORG}/api/v1/users/"
users = manage_data("GET", url)
for user in users:
    user_id = user["id"]
    first_name = user['profile']['firstName']
    last_name = user['profile']['lastName']
    primary_email = user['profile']['email']
    print(f"Name:{first_name} {last_name}\nID:{user_id}\nPrimary Email:{primary_email}\n")