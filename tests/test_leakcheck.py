import unittest
from unittest.mock import patch, MagicMock
from src.providers.leakcheck_client import LeakCheckClient


class TestLeakCheckClient(unittest.TestCase):

    @patch("src.providers.leakcheck_client.requests.get")
    def test_parses_success_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "found": 2,
            "sources": [{"name": "example.com"}, {"name": "test.com"}]
        }

        mock_get.return_value = mock_response

        client = LeakCheckClient("http://fake-url", 5)
        result = client.check_email("test@example.com")

        self.assertTrue(result["breached"])
        self.assertEqual(result["breach_count"], 2)
        self.assertEqual(result["sources"], ["example.com", "test.com"])

    @patch("src.providers.leakcheck_client.requests.get")
    def test_no_breaches(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"found": 0}

        mock_get.return_value = mock_response

        client = LeakCheckClient("http://fake-url", 5)
        result = client.check_email("clean@example.com")

        self.assertFalse(result["breached"])
        self.assertEqual(result["breach_count"], 0)

    def test_leakcheck_handles_rate_limit(self):

        client = LeakCheckClient("test_key", 10)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_get.return_value = mock_response

            with self.assertRaises(Exception):
                client.check_email("test@example.com")