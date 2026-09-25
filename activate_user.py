import argparse
import os
import sys
from dotenv import load_dotenv
from manage import manage_data

load_dotenv()

ORG = os.environ["OKTA_ORG_URL"]

def activate_user(login: str, confirm: bool):
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
        print("Token owner cannot be modified.")
        sys.exit(1)

    if status == "PROVISIONED":
        print(f"[SKIP] {first_name} {last_name} has a pending activation.")
        return
    elif status == "ACTIVE":
        print(f"[SKIP] {first_name} {last_name} is already activated.")
        return
    elif status == "PASSWORD_EXPIRED":
        print(f"[SKIP] {first_name} {last_name} already activated. Must change password at next login. No changes made.")
        return

    if status == "DEPROVISIONED" or status == "STAGED":
        if not confirm:
            print(
                f"[DRY RUN] Safe Mode: User '{first_name} {last_name}' ({login}) with status '{status}' would be activated.")
            print("[DRY RUN] No changes were made. Run with --confirm to execute.")
            return

        url_a = f"{ORG}/api/v1/users/{user_id}/lifecycle/activate"
        manage_data("POST", url_a, params={"sendEmail": 'true'})
        user_data = manage_data("GET", url_user)

        if user_data["status"] == "PROVISIONED":
            print("Check status:", user_data["status"])
            print(f"[EXECUTE] Successfully provisioned user {first_name} {last_name}.")
            print("Sent activation email to user's primary email.")
        else:
            print("Check status:", user_data["status"])
            print(f"[EXECUTE] Failed to activate user {first_name} {last_name}.")
            sys.exit(1)
    else:
        print(f"{first_name} {last_name} has a status of '{status}'. Different tool required.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Activate user")

    parser.add_argument(
        "login",
        type=str,
        help="The login of the account to activate."
    )

    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Explicitly confirm and execute the activation (disables dry-run)."
    )

    args = parser.parse_args()
    activate_user(args.login, args.confirm)


if __name__ == "__main__":
    main()
