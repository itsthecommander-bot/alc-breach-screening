"""
Defines the base class for each provider.
"""

from abc import ABC, abstractmethod

class BaseProvider(ABC):

    @abstractmethod
    def check_email(self, email: str) -> dict:
        pass