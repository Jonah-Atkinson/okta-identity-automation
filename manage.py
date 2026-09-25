import os
import json
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

ORG = os.environ["OKTA_ORG_URL"]
TOKEN = os.environ["OKTA_API_TOKEN"]

headers = {
    "Authorization": f"SSWS {TOKEN}",
    "Accept": "application/json",
}

def manage_data(method, url, params=None):
    try:
        response = requests.request(method, url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout as err:
        print(f"Error: Network timed out and took too long to respond.")
        sys.exit(1)
    except requests.exceptions.ConnectionError as err:
        print(f"Error: Could not connect to Okta API.")
        sys.exit(1)
    except requests.exceptions.HTTPError as err:
        try:
            status_code = err.response.status_code
            error_json = err.response.json()
            error_summary = error_json.get("errorSummary", "No summary provided by Okta.")
            print(f"{status_code} {error_summary}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error parsing JSON: {err}")
            sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(f"Error: Could not connect to Okta API: {err}")
        sys.exit(1)