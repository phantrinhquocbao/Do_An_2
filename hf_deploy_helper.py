import json
import os
import sys

import requests


API_BASE = "https://huggingface.co/api"


def safe_print(text: str) -> None:
    print(text.encode("ascii", "backslashreplace").decode("ascii"))


def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def whoami(token: str) -> int:
    response = requests.get(f"{API_BASE}/whoami-v2", headers=get_headers(token), timeout=30)
    print(response.status_code)
    safe_print(response.text)
    return 0 if response.ok else 1


def create_space(token: str, name: str, sdk: str = "docker") -> int:
    payload = {"type": "space", "name": name, "sdk": sdk}
    response = requests.post(
        f"{API_BASE}/repos/create",
        headers={**get_headers(token), "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )
    print(response.status_code)
    safe_print(response.text)
    return 0 if response.ok else 1


def space_info(token: str, repo_id: str) -> int:
    response = requests.get(f"{API_BASE}/spaces/{repo_id}", headers=get_headers(token), timeout=30)
    print(response.status_code)
    safe_print(response.text)
    return 0 if response.ok else 1


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: hf_deploy_helper.py <whoami|create-space> <token> [space_name]")
        return 2

    action = sys.argv[1]
    token = sys.argv[2]

    if action == "whoami":
        return whoami(token)

    if action == "create-space":
        if len(sys.argv) < 4:
            print("Missing space name")
            return 2
        return create_space(token, sys.argv[3])

    if action == "space-info":
        if len(sys.argv) < 4:
            print("Missing repo id")
            return 2
        return space_info(token, sys.argv[3])

    print(f"Unknown action: {action}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
