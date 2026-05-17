import os
from unittest import mock
from dotenv import load_dotenv

from app.services.llm_client import LLMClient, LLMConnectionError, LLMResponseError

# Cargar variables de entorno desde .env para pruebas que dependen de configuración
load_dotenv()


class DummyChoice:
    def __init__(self, text):
        class Msg:
            def __init__(self, content):
                self.content = content

        self.message = Msg(text)


class DummyResponse:
    def __init__(self, text):
        self.choices = [DummyChoice(text)]


def test_llm_client_returns_content(monkeypatch, tmp_path):
    # Usar variables reales desde .env (mock del cliente OpenAI sigue aplicado)

    # Mock OpenAI client
    class MockChat:
        class completions:
            @staticmethod
            def create(**kwargs):
                return DummyResponse("OK_RESPONSE")

    class MockClient:
        chat = MockChat()

    monkeypatch.setattr("app.services.llm_client.OpenAI", lambda *args, **kwargs: MockClient())

    client = LLMClient()
    content = client.chat_completion(messages=[{"role": "user", "content": "Hola"}], model="deployment")
    assert content == "OK_RESPONSE"


def test_llm_client_retries_on_error(monkeypatch):
    # Variables de entorno se cargan desde .env

    calls = {"count": 0}

    class FlakyChat:
        class completions:
            @staticmethod
            def create(**kwargs):
                calls["count"] += 1
                if calls["count"] < 2:
                    raise RuntimeError("transient")
                return DummyResponse("RECOVERED")

    class MockClient:
        chat = FlakyChat()

    monkeypatch.setattr("app.services.llm_client.OpenAI", lambda *args, **kwargs: MockClient())

    client = LLMClient(max_retries=2)
    content = client.chat_completion(messages=[{"role": "user", "content": "Hola"}], model="deployment")
    assert content == "RECOVERED"
    assert calls["count"] == 2


def test_llm_client_raises_on_bad_response(monkeypatch):
    # Variables de entorno se cargan desde .env

    class EmptyResponse:
        def __init__(self):
            self.choices = []

    class MockClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    return EmptyResponse()

    monkeypatch.setattr("app.services.llm_client.OpenAI", lambda *args, **kwargs: MockClient())

    client = LLMClient()
    try:
        client.chat_completion(messages=[{"role": "user", "content": "Hola"}], model="deployment")
        assert False, "Expected LLMResponseError"
    except LLMResponseError:
        pass
