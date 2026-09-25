import os
import sys
from dotenv import load_dotenv
import argparse
from manage import manage_data

load_dotenv()

ORG = os.environ["OKTA_ORG_URL"]

def deactivate_user(login: str, confirm: bool):
    url_token_user = f"{ORG}/api/v1/users/me"
    url_user = f"{ORG}/api/v1/users/{login}"
    token_user = manage_data("GET", url_token_user)
    token_user_id = token_user["id"]

    user_data = manage_data("GET", url_user)
    first_name = user_data["profile"]["firstName"]
    last_name = user_data["profile"]["lastName"]
    user_id = user_data["id"]
    status = user_data['status']
    if token_user_id == user_id:
        print("Cannot deactivate current token owner.")
        sys.exit(1)
# Check if user is deactivated already to move on quickly.
    if status == "DEPROVISIONED":
        print(f"{first_name} {last_name} already deactivated.")
        return

    if not confirm:
        print(
            f"[DRY RUN] Safe Mode: User '{first_name} {last_name}' ({login}) with status '{status}' would be deactivated.")
        print("[DRY RUN] No changes were made. Run with --confirm to execute.")
        return

    url_d = f"{ORG}/api/v1/users/{user_id}/lifecycle/deactivate"
    manage_data("POST", url_d)
    user_data = manage_data("GET", url_user)

    if user_data["status"] == "DEPROVISIONED":
        print("Check status:", user_data["status"])
        print(f"[EXECUTE] Successfully deactivated user {first_name} {last_name} from the system.")
    else:
        print("Check status:", user_data["status"])
        print(f"[EXECUTE] Failed to deactivate user {first_name} {last_name}.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Deactivate user")

    parser.add_argument(
        "login",
        type=str,
        help="The login of the account to deactivate."
    )

    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Explicitly confirm and execute the deactivation (disables dry-run)."
    )

    args = parser.parse_args()
    deactivate_user(args.login, args.confirm)


if __name__ == "__main__":
    main()