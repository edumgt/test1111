import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from krx_daily_api import get_krx_key


class GetKrxKeyTests(unittest.TestCase):
    def test_reads_trimmed_codespaces_secret_from_environment(self) -> None:
        with patch.dict(os.environ, {"KRX_KEY": "  codespaces-secret  "}):
            self.assertEqual(get_krx_key(), "codespaces-secret")

    def test_whitespace_environment_value_falls_back_to_key_file(self) -> None:
        with TemporaryDirectory() as directory:
            key_file = Path(directory) / ".key"
            key_file.write_text("KRX-KEY=local-secret\n", encoding="utf-8")
            with patch.dict(os.environ, {"KRX_KEY": "   "}):
                with patch("krx_daily_api.KEY_FILE", key_file):
                    self.assertEqual(get_krx_key(), "local-secret")
