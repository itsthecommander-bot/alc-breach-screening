import os
import time
import requests
from dotenv import load_dotenv
from src.providers.base_provider import BaseProvider

class IntelXClient(BaseProvider):

    def __init__(self, base_url: str, timeout: int):
        load_dotenv()
        self.api_key = os.getenv("INTELX_API_KEY")
        self.base_url = base_url
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("INTELX_API_KEY not found in environment variables.")

    def _handle_response(self, response, step_name: str):
        if response.status_code == 429:
            raise Exception(f"IntelX rate limit exceeded (429) during {step_name}")

        if response.status_code != 200:
            raise Exception(
                f"IntelX {step_name} error: {response.status_code} - {response.text}"
            )

    def check_email(self, email: str) -> dict:

        headers = {
            "x-key": self.api_key,
            "Content-Type": "application/json"
        }

        search_payload = {
            "term": email,
            "maxresults": 10,
            "media": 0,
            "target": 2,
            "timeout": 20,
            "datefrom": "",
            "dateto": "",
            "sort": 0
        }

        response = requests.post(
            f"{self.base_url}/intelligent/search",
            headers=headers,
            json=search_payload,
            timeout=self.timeout
        )

        self._handle_response(response, "search")

        data = response.json()
        search_id = data.get("id")

        if not search_id or search_id == "00000000-0000-0000-0000-000000000000":
            return {
                "email": email,
                "breached": False,
                "breach_count": 0,
                "sources": []
            }

        time.sleep(2)

        result_response = requests.get(
            f"{self.base_url}/intelligent/search/result",
            headers=headers,
            params={"id": search_id},
            timeout=self.timeout
        )

        self._handle_response(result_response, "result")

        result_data = result_response.json()

        records = result_data.get("records", [])

        clean_sources = []

        for record in records:
            name = record.get("name", "")
            bucket = record.get("bucket", "")

            if "leak" in bucket.lower() or "paste" in bucket.lower() or "dump" in bucket.lower():

                if name.startswith("http"):
                    domain = name.split("/")[2]
                    clean_sources.append(domain)

                else:
                    cleaned = name.split("/")[-1]
                    cleaned = cleaned.split(" ")[0]

                    for ext in [".sql", ".txt", ".csv"]:
                        if cleaned.lower().endswith(ext):
                            cleaned = cleaned[:-len(ext)]

                    if "." in cleaned:
                        clean_sources.append(cleaned)

        clean_sources = list(dict.fromkeys(clean_sources))

        return {
            "email": email,
            "breached": len(clean_sources) > 0,
            "breach_count": len(clean_sources),
            "sources": clean_sources[:50]
        }