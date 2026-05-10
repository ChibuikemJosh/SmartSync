import os

import requests
from fastapi import HTTPException


def _headers() -> dict:
    squad_secret_key = os.getenv("SQUAD_SECRET_KEY", "")
    headers = {"Content-Type": "application/json"}
    if squad_secret_key:
        headers["Authorization"] = f"Bearer {squad_secret_key}"
    return headers


def _post(endpoint: str, payload: dict) -> dict:
    squad_base_url = os.getenv("SQUAD_BASE_URL", "https://sandbox-api-d.squadco.com")
    try:
        response = requests.post(
            f"{squad_base_url}{endpoint}",
            json=payload,
            headers=_headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else 502
        client_status_code = status_code if 400 <= status_code <= 499 else 502
        raise HTTPException(
            status_code=client_status_code,
            detail=f"Squad API request failed (upstream status: {status_code})",
        ) from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Squad API request failed") from exc


def create_virtual_account(payload: dict) -> dict:
    return _post("/virtual-account", payload)


def generate_payment_link(payload: dict) -> dict:
    return _post("/payment-link", payload)
