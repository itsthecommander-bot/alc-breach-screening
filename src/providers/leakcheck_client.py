"""
Used to query the LeakCheck API for email breach information.
"""

import os
import requests
from dotenv import load_dotenv
from src.providers.base_provider import BaseProvider

class LeakCheckClient(BaseProvider):
    def __init__(self, base_url: str, timeout: int):
        load_dotenv()
        self.api_key = os.getenv("LEAKCHECK_API_KEY")
        self.base_url = base_url
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("LEAKCHECK_API_KEY not found in environment variables.")

    def check_email(self, email: str) -> dict:
        headers = {
            "X-API-Key": self.api_key
        }

        params = {
            "check": email
        }

        response = requests.get(
            self.base_url,
            headers=headers,
            params=params,
            timeout=self.timeout
        )

        if response.status_code == 429:
            raise Exception("LeakCheck rate limit exceeded (429)")
        
        if response.status_code == 200:
            data = response.json()

            found = data.get("found", 0)
            sources = []

            if found > 0:
                results = data.get("sources", [])
                sources = [entry.get("name") for entry in results if entry.get("name")]

            sources = sources[:50]

            return {
                "email": email,
                "breached": len(sources) > 0,
                "breach_count": len(sources),
                "sources": sources
            }

        elif response.status_code == 404:
            return {
                "email": email,
                "breached": False,
                "sources": []
            }

        else:
            raise Exception(
                f"LeakCheck API error: {response.status_code} - {response.text}"
            )