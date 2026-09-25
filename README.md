# Okta Identity Automation

## What this does
Python scripts that automate common Okta admin tasks through Okta's API: list users, find specific user, and activate / deactivate (with a confirmation step) users.
Built and tested using the free Okta Integrator with test users only. It's the first part of a larger JML automation (see roadmap).

## Example output
``` 
python deactivate_user.py jane@example.com
[DRY RUN] Safe Mode: User 'Jane Dane' (jane@example.com) with status 'PASSWORD_EXPIRED' would be deactivated.
[DRY RUN] No changes were made. Run with --confirm to execute.

python deactivate_user.py jane@example.com --confirm
Check status: DEPROVISIONED
[EXECUTE] Successfully deactivated user Jane Dane from the system.
```

## Setup (tested on Python 3.14)
1. Clone the repo
2. Create a free Okta Integrator account, then create an API token under Security > API > Tokens
3. Install requirements: `pip install -r requirements.txt`
4. Copy .env.example to .env and add your Okta org URL and API token
5. Run any script

## Scripts
### list_users.py
Lists first page of users: first/last name, ID, and email. 
- Retrieves first page only, pagination planned in roadmap.
- Excludes deprovisioned accounts from the output (Okta default).

### get_user.py
Fetches specific user when searching by their login (retrieves first and last name, as well as their ID).

### manage.py
  - Shared function to request data and handle any errors that are thrown.
  - Provides information when HTTP, Request, Connection or Timeout errors occur.
  - Can work with both get and post requests, as well as any params the methods call for.
### activate_user.py
Moves a user to PROVISIONED (activation pending until they complete setup from the email). 
  - Sends email to user to set up their password, tested with real testing email. 
  - Skips provisioned, active and password_expired users with exit code 0 as to not run unnecessarily. 
  - Runs as a DRY RUN by default and uses --confirm to fully execute the script.
  - Has a guard to refuse the token owner's account and returns with exit code 1.
  - Uses error handling as to not cause a traceback. 
  - Gives proof of execution by printing user status and action taken.
  - Refuses any other status (e.g. SUSPENDED) and exits 1.


#### activate_user.py checks

| # | Scenario | How it was triggered | Output                                                                                                                                   | Exit |
|---|---|---|------------------------------------------------------------------------------------------------------------------------------------------|---|
| 1 | Unknown user | Login that doesn't exist | `404 Not found: Resource not found: fdsa@example.com (User)`                                                                             | 1 |
| 2 | Bad or expired token | Altered one character of the token in `.env` | `401 Invalid token provided`                                                                                                             | 1 |
| 3 | Network down | Wi-Fi disabled | `Error: Could not connect to Okta API.`                                                                                                  | 1 |
| 4 | Okta not responding | Temporarily set request timeout to 0.001s | `Error: Network timed out and took too long to respond.`                                                                                 | 1 |
| 5 | Dry run (default) | DEPROVISIONED user, no `--confirm` | `[DRY RUN] ... with status 'DEPROVISIONED' would be activated.` / `No changes were made.`                                                | 0 |
| 6 | Activate from DEPROVISIONED | Same user with `--confirm` | `Check status: PROVISIONED` / `[EXECUTE] Successfully provisioned user Bob Smith.`   /  `Sent activation email to user's primary email.` | 0 |
| 7 | Activate from STAGED | User added in Admin Console with "Activate now" unchecked, `--confirm` | `Check status: PROVISIONED` / `[EXECUTE] Successfully provisioned user Billy Smith.` / `Sent activation email to user's primary email.`  | 0 |
| 8 | Activation already pending (idempotent) | Same user as #6 again with `--confirm` | `[SKIP] Bob Smith has a pending activation.`                                                                                             | 0 |
| 9 | Already active | ACTIVE user with `--confirm` | `[SKIP] Jane Dane is already activated.`                                                                                                 | 0 |
| 10 | Password expired | User with an admin-set temporary password, with and without `--confirm` | `[SKIP] Bob Smith already activated. Must change password at next login. No changes made.`                                               | 0 |
| 11 | Unsupported status | SUSPENDED user with `--confirm` | `Jane Dane has a status of 'SUSPENDED'. Different tool required.`                                                                        | 1 |
| 12 | Token-owner guard | Token owner's own login | `Token owner cannot be modified.`                                                                                                        | 1 |
| 13 | Guard fails closed | `/users/me` URL deliberately broken | `404 Not found: Resource not found: mex (User)`; stops before the target user is touched                                                 | 1 |
| 14 | End to end | Plus-addressed test user, `--confirm`, then completed setup from the email | Email arrived, setup completed, re-fetch shows `ACTIVE`                                                                                  | 0 |

  **Design notes behind the results**
-   Success in #6 and #7 is confirmed by re-fetching the user, not by the HTTP 200. PROVISIONED is the correct result: activation stays pending until the user completes setup, which #14 proves end to end.
  - #8–#10 exit 0 without sending any request because the goal already holds. A PASSWORD_EXPIRED user has already been activated.
  - #11 exits 1 and names the status: the script refuses states it wasn't built for instead of guessing.
  - #13: the token owner is looked up first, so if that lookup fails the script stops before it touches anyone.


### deactivate_user.py
  - Uses a DRY RUN to show what action would be done first before confirming. Using --confirm will make the action take effect.
  - Takes login for user input and converts that to ID, and all actions are taken on that ID.
  - Includes self-lockout to not deactivate the current token owner's account. 
  - Checks for status before actions are taken to ensure deactivation is required. 
  - Gives verified proof of execution by reading the user's info, and their current status, back to the console.


#### deactivate_user.py checks

| # | Scenario | How it was triggered | Output | Exit |
|---|---|---|---|---|
| 1 | Unknown user | Login that doesn't exist | `404 Not found: Resource not found: nobody@example.com (User)` | 1 |
| 2 | Bad or expired token | Altered one character of the token in `.env` | `401 Invalid token provided` | 1 |
| 3 | Network down | Wi-Fi disabled | `Error: Could not connect to Okta API.` | 1 |
| 4 | Okta not responding | Temporarily set request timeout to 0.001s | `Error: Network timed out and took too long to respond.` | 1 |
| 5 | Dry run (default) | Active user, no `--confirm` | `[DRY RUN] ... would be deactivated. No changes were made.` | 0 |
| 6 | Deactivation | Same user with `--confirm` | `Check status: DEPROVISIONED` / `Successfully deactivated user` | 0 |
| 7 | Already deactivated (idempotent) | Same user again with `--confirm` | `Jane Dane already deactivated.` | 0 |
| 8 | Self-lockout guard | Token owner's own login, lowercase and uppercase | `Cannot deactivate current token owner.` | 1 |
| 9 | Guard fails closed | Token-owner lookup deliberately broken | Clean error and stop; no deactivation attempted | 1 |

**Design notes behind the results**
- Success in #6 is confirmed by re-fetching the user after the request, not by the HTTP 200.
- #7 exits 0 on purpose: the goal state already holds, so the script treats it as done.
- #8 compares user **ids**, not login strings, so case differences can't bypass the guard.
- #9 means if the script can't verify who owns the token, it refuses rather than proceeding.

## Security notes
Currently, the application uses an API Token with super admin privileges, because my account as the super admin created it.
A better solution would be to use OAuth 2.0 (Okta's recommendation) in order to give scoped access and 
a rotating token that expires after 1 hour. A private key or client secret is still needed and thus must still need protecting. OAuth is set according to what is needed per application, meaning get_user would only need okta.users.read, while deactivate_user needs okta.users.manage. 

An early version used sendEmail=false, which made Okta return a live activation token (enough for anyone holding it to complete account setup), and the script printed it to the console. Fixed by switching to sendEmail=true so Okta emails the link instead. Only test users were involved, and the output never left my machine.

A later refactor passed the headers dict into manage_data's params argument, which would have sent the API token as a URL query parameter, where it can end up in server and proxy logs. Caught in code review, fixed by letting manage.py own the auth header, and the token was rotated as a precaution.

Secrets are also stored in .env, with an example being provided in .env.example for others to paste their own secrets.

## Roadmap
1. Create joiner that creates a user and assigns them based on department.
2. Create mover that assigns new group membership based on role change.
3. Setting up OAuth 2.0 in place of API Token.
4. Combine scripts into one tool that can be called in the command line using commands for each action.
5. Create log file that records each change made, by who, and when, to leave an audit trail.
6. Ability to read from CSV and take the specified action on each user. 
7. Pagination when requesting more than 1 page of data.