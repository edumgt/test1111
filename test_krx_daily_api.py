import os
import unittest
from unittest.mock import patch

from krx_daily_api import get_krx_key


class GetKrxKeyTests(unittest.TestCase):
    def test_reads_trimmed_codespaces_secret_from_environment(self) -> None:
        with patch.dict(os.environ, {"KRX_KEY": "  codespaces-secret  "}):
            self.assertEqual(get_krx_key(), "codespaces-secret")
