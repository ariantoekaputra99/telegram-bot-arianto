import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bot_telegram import (  # noqa: E402
    build_application,
    contains_blocked_content,
    filter_messages,
    is_unsupported_language,
)


def test_blocks_http_links():
    assert contains_blocked_content("cek https://example.com") is True


def test_blocks_www_links():
    assert contains_blocked_content("kunjungi www.example.com") is True


def test_blocks_mentions():
    assert contains_blocked_content("hubungi @example_user") is True


def test_allows_normal_text():
    assert contains_blocked_content("Halo semuanya, selamat datang!") is False


@pytest.mark.parametrize(
    "text",
    [
        "Este es un mensaje escrito completamente en español para el grupo.",
        "Ceci est un message entièrement écrit en français pour le groupe.",
    ],
)
def test_blocks_confidently_detected_unsupported_languages(text):
    assert is_unsupported_language(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "Halo semuanya, selamat datang di grup kita hari ini.",
        "Hello everyone, welcome to our group today.",
    ],
)
def test_allows_indonesian_and_english(text):
    assert is_unsupported_language(text) is False


def test_allows_short_or_uncertain_text():
    assert is_unsupported_language("Hola amigo") is False
    assert is_unsupported_language("12345") is False


def test_deletes_forwarded_media_from_non_admin():
    message = SimpleNamespace(
        text=None,
        caption=None,
        forward_origin=object(),
        delete=AsyncMock(),
    )
    chat = SimpleNamespace(id=-100)
    user = SimpleNamespace(id=42)
    context = SimpleNamespace(
        bot=SimpleNamespace(
            get_chat_administrators=AsyncMock(return_value=[]),
            send_message=AsyncMock(),
        )
    )
    update = SimpleNamespace(
        effective_message=message,
        effective_chat=chat,
        effective_user=user,
    )

    asyncio.run(filter_messages(update, context))

    message.delete.assert_awaited_once()


def test_deletes_message_in_unsupported_language():
    message = SimpleNamespace(
        text="Este es un mensaje escrito completamente en español para el grupo.",
        caption=None,
        forward_origin=None,
        delete=AsyncMock(),
    )
    context = SimpleNamespace(
        bot=SimpleNamespace(
            get_chat_administrators=AsyncMock(return_value=[]),
            send_message=AsyncMock(),
        )
    )
    update = SimpleNamespace(
        effective_message=message,
        effective_chat=SimpleNamespace(id=-100),
        effective_user=SimpleNamespace(id=42),
    )

    asyncio.run(filter_messages(update, context))

    message.delete.assert_awaited_once()


def test_admin_forward_is_not_deleted():
    message = SimpleNamespace(
        text=None,
        caption=None,
        forward_origin=object(),
        delete=AsyncMock(),
    )
    admin = SimpleNamespace(user=SimpleNamespace(id=42))
    context = SimpleNamespace(
        bot=SimpleNamespace(
            get_chat_administrators=AsyncMock(return_value=[admin]),
            send_message=AsyncMock(),
        )
    )
    update = SimpleNamespace(
        effective_message=message,
        effective_chat=SimpleNamespace(id=-100),
        effective_user=SimpleNamespace(id=42),
    )

    asyncio.run(filter_messages(update, context))

    message.delete.assert_not_awaited()


def test_build_application_requires_token(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
        build_application()
