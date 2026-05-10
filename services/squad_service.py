import os

import requests
from fastapi import HTTPException


SQUAD_BASE_URL = os.getenv("SQUAD_BASE_URL", "https://sandbox-api-d.squadco.com")
SQUAD_SECRET_KEY = os.getenv("SQUAD_SECRET_KEY", "")


def _headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if SQUAD_SECRET_KEY:
        headers["Authorization"] = f"Bearer {SQUAD_SECRET_KEY}"
    return headers


def _post(endpoint: str, payload: dict) -> dict:
    try:
        response = requests.post(
            f"{SQUAD_BASE_URL}{endpoint}",
            json=payload,
            headers=_headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else 502
        raise HTTPException(
            status_code=502,
            detail=f"Squad API request failed (upstream status: {status_code})",
        ) from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Squad API request failed") from exc


def create_virtual_account(payload: dict) -> dict:
    return _post("/virtual-account", payload)


def generate_payment_link(payload: dict) -> dict:
    return _post("/payment-link", payload)
