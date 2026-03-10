import unittest
import io
from unittest.mock import patch, mock_open, MagicMock
from src.main import process_emails


class TestMain(unittest.TestCase):

    @patch("src.main.ScreeningService")
    @patch("src.main.csv.DictReader")
    @patch("src.main.open")
    def test_process_single_email_success(
        self, mock_open, mock_dictreader, mock_service_class
    ):
        mock_reader = MagicMock()
        mock_reader.fieldnames = ["email_address"]
        mock_reader.__iter__.return_value = [
            {"email_address": "example@test.com"}
        ]

        mock_dictreader.return_value = mock_reader

        mock_service = MagicMock()
        mock_service.check_email.return_value = {
            "breached": True,
            "breach_count": 2,
            "sources": ["example.com", "test.com"],
            "provider": "LeakCheck"
        }

        mock_service_class.return_value = mock_service

        process_emails()

        mock_service.check_email.assert_called_once_with("example@test.com")

    @patch("src.main.ScreeningService")
    @patch("src.main.csv.DictReader")
    @patch("src.main.open")
    def test_process_email_handles_exception(
        self, mock_open, mock_dictreader, mock_service_class
    ):
        mock_reader = MagicMock()
        mock_reader.fieldnames = ["email_address"]
        mock_reader.__iter__.return_value = [
            {"email_address": "bad@test.com"}
        ]

        mock_dictreader.return_value = mock_reader

        mock_service = MagicMock()
        mock_service.check_email.side_effect = Exception("API failure")

        mock_service_class.return_value = mock_service

        process_emails()

        mock_service.check_email.assert_called_once_with("bad@test.com")

    @patch("src.main.ScreeningService")
    def test_csv_output_content(self, mock_service_class):

        import io
        from unittest.mock import patch

        mock_service = MagicMock()
        mock_service.check_email.return_value = {
            "breached": True,
            "breach_count": 2,
            "sources": ["example.com", "test.com"],
            "provider": "LeakCheck"
        }

        mock_service_class.return_value = mock_service

        input_data = "email_address\nexample@test.com\n"
        input_file = io.StringIO(input_data)
        output_file = io.StringIO()

        output_file.close = lambda: None

        def mocked_open(file, mode="r", *args, **kwargs):
            if "r" in mode:
                return input_file
            elif "w" in mode:
                return output_file
            else:
                raise ValueError("Unsupported mode")

        with patch("builtins.open", side_effect=mocked_open):
            process_emails()

        output_content = output_file.getvalue()

        self.assertIn("email_address", output_content)
        self.assertIn("breach_count", output_content)
        self.assertIn("provider_used", output_content)
        self.assertIn("example@test.com", output_content)
        self.assertIn("True", output_content)
        self.assertIn("2", output_content)
        self.assertIn("example.com;test.com", output_content)

    @patch("src.main.csv.DictReader")
    @patch("src.main.open")
    def test_missing_email_column(self, mock_open, mock_dictreader):

        mock_reader = MagicMock()
        mock_reader.fieldnames = ["name"]  # Missing email column
        mock_reader.__iter__.return_value = []

        mock_dictreader.return_value = mock_reader

        with self.assertRaises(ValueError):
            process_emails()