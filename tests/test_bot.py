import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bot_telegram import build_application, contains_blocked_content  # noqa: E402


def test_blocks_http_links():
    assert contains_blocked_content("cek https://example.com") is True


def test_blocks_www_links():
    assert contains_blocked_content("kunjungi www.example.com") is True


def test_blocks_mentions():
    assert contains_blocked_content("hubungi @example_user") is True


def test_allows_normal_text():
    assert contains_blocked_content("Halo semuanya, selamat datang!") is False


def test_build_application_requires_token(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
        build_application()
