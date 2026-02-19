from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass(frozen=True)
class MetaWhatsAppConfig:
    access_token: str
    phone_number_id: str
    api_version: str = "v22.0"

    @property
    def base_url(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}"


class MetaWhatsAppAPIError(Exception):
    def __init__(self, message: str, status_code: int, response_text: str):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class MetaWhatsAppService:
    def __init__(self, config: MetaWhatsAppConfig, session: Optional[requests.Session] = None):
        self.config = config
        self.session = session or requests.Session()

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
        }

    def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        url = f"{self.config.base_url}/{self.config.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }

        response = self.session.post(url, headers=self._headers(), json=payload, timeout=15)

        if 200 <= response.status_code < 300:
            return response.json()

        # Safe log (no token printed)
        print(f"[META] send_text_message failed status={response.status_code} body={response.text}")

        raise MetaWhatsAppAPIError(
            "Meta API request failed",
            response.status_code,
            response.text,
        )
