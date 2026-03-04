import unittest
from unittest.mock import patch, MagicMock
from src.providers.intelx_client import IntelXClient


class TestIntelXClient(unittest.TestCase):

    @patch("src.providers.intelx_client.time.sleep", return_value=None)
    @patch("src.providers.intelx_client.requests.get")
    @patch("src.providers.intelx_client.requests.post")
    @patch("src.providers.intelx_client.os.getenv", return_value="fake-key")
    def test_parses_records_and_deduplicates(
        self,
        mock_getenv,
        mock_post,
        mock_get,
        mock_sleep
    ):

        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "id": "abc123"
        }
        mock_post.return_value = mock_post_response

        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "records": [
                {
                    "name": "example.com.txt",
                    "bucket": "leak-database"
                },
                {
                    "name": "example.com.txt",
                    "bucket": "leak-database"
                },
                {
                    "name": "test.com.sql",
                    "bucket": "dump-files"
                }
            ]
        }
        mock_get.return_value = mock_get_response

        client = IntelXClient("http://fake-url", 5)
        result = client.check_email("test@example.com")

        self.assertTrue(result["breached"])
        self.assertEqual(result["breach_count"], 2)
        self.assertIn("example.com", result["sources"])
        self.assertIn("test.com", result["sources"])