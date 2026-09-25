import argparse
import os
from dotenv import load_dotenv
from manage import manage_data


load_dotenv()

ORG = os.environ["OKTA_ORG_URL"]

def get_user(login: str):
    url = f"{ORG}/api/v1/users/{login}"
    user = manage_data("GET", url)
    user_id = user['id']
    first_name = user['profile']['firstName']
    last_name = user['profile']['lastName']

    print(f"Name: {first_name} {last_name}\n"
          f"ID: {user_id}")

def main():
    parser = argparse.ArgumentParser(description="Get specific user")

    parser.add_argument(
        "login",
        type=str,
        help="The login of the account to find."
    )

    args = parser.parse_args()
    get_user(args.login)


if __name__ == "__main__":
    main()