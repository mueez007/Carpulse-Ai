import os
import requests

MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")


def send_make_webhook(email: str, full_name: str, user_id: int) -> None:
    """
    Send a POST request to the Make webhook URL with new user data.
    This runs as a background task; exceptions are caught and logged.
    """
    if not MAKE_WEBHOOK_URL:
        print("MAKE_WEBHOOK_URL not configured; skipping Make webhook.")
        return

    payload = {
        "event": "user_registered",
        "user": {
            "id": user_id,
            "email": email,
            "full_name": full_name,
        },
    }

    try:
        resp = requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=5)
        if resp.status_code >= 400:
            print(f"Make webhook returned status {resp.status_code}: {resp.text}")
        else:
            print(f"Make webhook delivered: {resp.status_code}")
    except Exception as e:
        print(f"Error sending Make webhook: {e}")
