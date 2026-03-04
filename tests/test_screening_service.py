import unittest
from unittest.mock import patch, MagicMock
from src.screening_service import ScreeningService


class TestScreeningService(unittest.TestCase):

    @patch("src.screening_service.LeakCheckClient")
    @patch("src.screening_service.IntelXClient")
    def test_leakcheck_success(self, mock_intelx, mock_leakcheck):
        mock_leakcheck_instance = MagicMock()
        mock_leakcheck_instance.check_email.return_value = {
            "email": "test@example.com",
            "breached": True,
            "breach_count": 2,
            "sources": ["example.com"]
        }
        mock_leakcheck.return_value = mock_leakcheck_instance

        service = ScreeningService()

        result = service.check_email("test@example.com")

        self.assertEqual(result["provider"], "LeakCheck")
        self.assertTrue(result["breached"])
        self.assertEqual(result["breach_count"], 2)


    @patch("src.screening_service.time.sleep", return_value=None)
    @patch("src.screening_service.LeakCheckClient")
    @patch("src.screening_service.IntelXClient")
    def test_fallback_to_intelx(
        self,
        mock_intelx,
        mock_leakcheck,
        mock_sleep
    ):

        mock_leakcheck_instance = MagicMock()
        mock_leakcheck_instance.check_email.side_effect = Exception("LeakCheck down")
        mock_leakcheck.return_value = mock_leakcheck_instance

        mock_intelx_instance = MagicMock()
        mock_intelx_instance.check_email.return_value = {
            "email": "test@example.com",
            "breached": False,
            "breach_count": 0,
            "sources": []
        }
        mock_intelx.return_value = mock_intelx_instance

        service = ScreeningService()

        result = service.check_email("test@example.com")

        self.assertEqual(result["provider"], "IntelX")
        self.assertFalse(result["breached"])

        self.assertEqual(
            mock_leakcheck_instance.check_email.call_count,
            3
        )

        self.assertEqual(mock_sleep.call_count, 2)


    @patch("src.screening_service.LeakCheckClient")
    @patch("src.screening_service.IntelXClient")
    def test_leakcheck_disabled_after_repeated_failures(self, mock_intelx, mock_leakcheck):

        mock_leakcheck_instance = MagicMock()
        mock_leakcheck_instance.check_email.side_effect = Exception("LeakCheck down")
        mock_leakcheck.return_value = mock_leakcheck_instance

        mock_intelx_instance = MagicMock()
        mock_intelx_instance.check_email.return_value = {
            "email": "test@example.com",
            "breached": False,
            "breach_count": 0,
            "sources": []
        }
        mock_intelx.return_value = mock_intelx_instance

        service = ScreeningService()


        for _ in range(4):
            service.check_email("test@example.com")

        self.assertTrue(service.provider_health["LeakCheck"]["disabled"])


if __name__ == "__main__":
    unittest.main()