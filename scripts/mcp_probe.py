import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()
URL = "https://factorweave.com/api/mcp"


def call(method: str, params: dict | None = None, request_id: int = 1) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    key = os.getenv("FACTORWEAVE_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params or {},
    }
    response = requests.post(URL, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    return response.json()


def main() -> None:
    init = call(
        "initialize",
        {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "ssushhii-factorweave-probe", "version": "0.1.0"},
        },
        1,
    )
    print("initialize:")
    print(json.dumps(init, indent=2)[:4000])

    tools = call("tools/list", {}, 2)
    print("\ntools/list:")
    print(json.dumps(tools, indent=2)[:8000])


if __name__ == "__main__":
    main()
