import yaml
import time
import logging

from src.providers.leakcheck_client import LeakCheckClient
from src.providers.intelx_client import IntelXClient

class ScreeningService:
    """
    Handles checking email addresses against the available breach providers
    and manages switching to a backup provider if one fails.
    """

    def __init__(self, primary_provider=None):
        """
        Initialise the service and load configuration for the API providers.
        """
        self.config = self._load_config()

        self.providers = {
            "LeakCheck": LeakCheckClient(
                base_url=self.config["api"]["leakcheck"]["base_url"],
                timeout=self.config["api"]["leakcheck"]["timeout"]
            ),
            "IntelX": IntelXClient(
                base_url=self.config["api"]["intelx"]["base_url"],
                timeout=self.config["api"]["intelx"]["timeout"]
            )
        }

        self.primary_provider = primary_provider or "LeakCheck"

        if self.primary_provider not in self.providers:
            raise ValueError(
                f"Invalid primary provider: {self.primary_provider}"
            )

        self.provider_health = {
            name: {"failures": 0, "disabled": False}
            for name in self.providers
        }

        self.max_failures = 3
        self.max_retries = 3
        self.backoff_factor = 2

    def _retry_with_backoff(self, func, provider_name, email):
        """
        Retry a provider request multiple times if it fails.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                return func(email)

            except Exception as e:
                logging.warning(
                    f"{provider_name} attempt {attempt} failed: {e}"
                )

                if attempt == self.max_retries:
                    logging.error(
                        f"{provider_name} failed after {self.max_retries} attempts"
                    )
                    raise

                sleep_time = self.backoff_factor ** (attempt - 1)
                logging.info(
                    f"Retrying {provider_name} in {sleep_time} seconds..."
                )
                time.sleep(sleep_time)

    def _load_config(self):
        """
        Load API settings from the config.yaml file.
        """
        with open("config.yaml", "r") as file:
            return yaml.safe_load(file)

    def check_email(self, email: str) -> dict:
        """
        Check an email address using the configured breach providers.
        If the primary provider fails, the backup provider will be used.
        """
        primary = self.primary_provider
        backup = next(p for p in self.providers if p != primary)

        for provider_name in [primary, backup]:

            provider_instance = self.providers[provider_name]

            if self.provider_health[provider_name]["disabled"]:
                continue

            try:
                logging.info(f"Using {provider_name}...")

                result = self._retry_with_backoff(
                    provider_instance.check_email,
                    provider_name,
                    email
                )

                self.provider_health[provider_name]["failures"] = 0
                logging.debug(f"Provider health state: {self.provider_health}")

                return {
                    "provider": provider_name,
                    **result
                }

            except Exception as e:
                logging.error(f"{provider_name} failed: {e}")

                self.provider_health[provider_name]["failures"] += 1

                if self.provider_health[provider_name]["failures"] >= self.max_failures:
                    self.provider_health[provider_name]["disabled"] = True
                    logging.warning(
                        f"{provider_name} temporarily disabled due to repeated failures"
                    )

        raise Exception("All providers failed.")