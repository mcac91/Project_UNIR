"""Cliente LLM centralizado para Azure OpenAI.

Implementación enfocada en Azure OpenAI (según indicación del usuario).
Provee manejo de timeouts, reintentos y excepciones específicas.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, List

from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - import errors handled at runtime
    OpenAI = None


logger = logging.getLogger(__name__)


class LLMConnectionError(RuntimeError):
    pass


class LLMResponseError(RuntimeError):
    pass


class LLMTimeoutError(RuntimeError):
    pass


class LLMClient:
    """Cliente simple para Azure OpenAI.

    Configuración a través de variables de entorno (ver `.env.example`).

    Ejemplo de uso:
        client = LLMClient()
        text = client.chat_completion(messages, model)
    """

    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str | None = None,
        api_version: str | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        load_dotenv()

        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.endpoint = endpoint or os.getenv("LLM_ENDPOINT")
        self.api_version = api_version or os.getenv("LLM_API_VERSION", "2024-10-21")
        self.timeout = int(timeout or os.getenv("LLM_TIMEOUT", "30"))
        self.max_retries = int(max_retries or os.getenv("LLM_MAX_RETRIES", "3"))

        if not all([self.api_key, self.endpoint]):
            raise LLMConnectionError("LLM_API_KEY y LLM_ENDPOINT deben estar configurados")

        if OpenAI is None:
            raise LLMConnectionError("Paquete 'openai' no está instalado")

        # Configurar cliente OpenAI para Azure
        try:
            import openai

            openai.api_key = self.api_key
            # Azure requiere base url con esquema: https://<name>.openai.azure.com/
            openai.api_base = self.endpoint
            # Indicar que es Azure
            openai.api_type = "azure"
            openai.api_version = self.api_version

            # Crear instancia del cliente
            self.client = OpenAI()
        except Exception as exc:  # pragma: no cover - environment dependent
            logger.exception("Error inicializando cliente OpenAI")
            raise LLMConnectionError(str(exc))

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> str:
        """Solicita una finalización de chat y devuelve el contenido del primer choice.

        Reintenta ante errores transitorios hasta `self.max_retries`.
        Lanza `LLMResponseError` si la respuesta no contiene el formato esperado.
        """
        attempt = 0
        last_exc: Exception | None = None

        while attempt <= self.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout,
                )

                # Navegar el objeto respuesta de forma robusta
                choices = getattr(response, "choices", None)
                if not choices:
                    raise LLMResponseError("Respuesta no contiene 'choices'")

                first = choices[0]
                # El SDK nuevo envuelve el contenido en .message.content
                content = None
                if hasattr(first, "message") and hasattr(first.message, "content"):
                    content = first.message.content
                elif isinstance(first, dict):
                    # fallback a dict shape
                    content = first.get("message", {}).get("content") or first.get("text")
                else:
                    content = getattr(first, "text", None)

                if not content:
                    raise LLMResponseError("No se pudo extraer contenido de la respuesta LLM")

                return content

            except LLMResponseError:
                raise
            except TimeoutError as e:
                last_exc = e
                logger.warning("Timeout en llamada LLM, intento %d", attempt)
                if attempt == self.max_retries:
                    raise LLMTimeoutError(str(e))
            except Exception as e:
                last_exc = e
                logger.warning("Error en llamada LLM (intento %d): %s", attempt, e)

            # Exponencial backoff
            wait = min(2 ** attempt, 10)
            time.sleep(wait)
            attempt += 1

        raise LLMConnectionError(f"Fallo en llamadas LLM tras {self.max_retries} reintentos: {last_exc}")
