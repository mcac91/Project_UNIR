"""Cliente LLM centralizado para Azure OpenAI.

Implementación enfocada en Azure OpenAI (según indicación del usuario).
Provee manejo de timeouts, reintentos y excepciones específicas.
"""
from __future__ import annotations

import logging
from pathlib import Path
import os
import time
from typing import Any, Dict, List

from dotenv import load_dotenv

from app.config.constants import DEFAULT_LLM_MODEL

try:
    from openai import AzureOpenAI, OpenAI
except Exception:  # pragma: no cover - import errors handled at runtime
    AzureOpenAI = None
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
        project_root = Path(__file__).resolve().parents[2]
        dotenv_path = project_root / ".env"
        load_dotenv(dotenv_path=dotenv_path)

        self.api_key = api_key or os.getenv("LLM_API_KEY")
        endpoint_value = endpoint or os.getenv("LLM_ENDPOINT")
        self.endpoint = endpoint_value.rstrip("/") if endpoint_value else endpoint_value

        self.api_version = api_version or os.getenv("LLM_API_VERSION", "2024-02-15-preview")

        self.default_model = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)
        self.timeout = int(timeout or os.getenv("LLM_TIMEOUT", "30"))
        self.max_retries = int(max_retries or os.getenv("LLM_MAX_RETRIES", "3"))

        if not all([self.api_key, self.endpoint]):
            raise LLMConnectionError("LLM_API_KEY y LLM_ENDPOINT deben estar configurados")

        if OpenAI is None:
                raise LLMConnectionError("Paquete 'openai' no está instalado")

        logger.info(
            "LLMClient init: endpoint=%r api_version=%r default_model=%r timeout=%r max_retries=%r",
            self.endpoint,
            self.api_version,
            self.default_model,
            self.timeout,
            self.max_retries,
        )
        logger.info(
            "LLMClient init: SDK flags OpenAI=%s AzureOpenAI=%s",
            OpenAI is not None,
            AzureOpenAI is not None,
        )

        # Configurar cliente para Azure.
        try:
            if AzureOpenAI is None:
                raise RuntimeError("No se pudo importar AzureOpenAI desde el SDK openai")

            logger.info("Inicializando AzureOpenAI (rama principal)")
            # SDK oficial: azure_endpoint + api_version.
            self.client = AzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.endpoint,
                api_version=self.api_version,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )
        except Exception as init_exc:
            logger.info(
                "Falló la inicialización de AzureOpenAI; entrando a fallback OpenAI. detalle=%s",
                init_exc,
            )
            # Fallback: por compatibilidad con versiones del SDK donde AzureOpenAI
            # no está disponible o no acepta parámetros de timeout/max_retries.
            
            # Fallback: por compatibilidad con versiones del SDK donde AzureOpenAI
            # no está disponible o no acepta parámetros de timeout/max_retries.
            try:
                if OpenAI is None:
                    raise RuntimeError("No se pudo importar OpenAI desde el SDK openai")

                logger.info("Inicializando OpenAI (fallback) con base_url y api-version")
                sep = "&" if "?" in self.endpoint else "?"
                base_url = f"{self.endpoint}{sep}api-version={self.api_version}"
                logger.info("LLMClient fallback base_url=%r", base_url)
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=base_url,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                )
            except Exception as exc:  # pragma: no cover - environment dependent
                logger.exception("Error inicializando cliente LLM")
                raise LLMConnectionError(str(exc)) from exc


        
    
    def chat_completion(

        self,
        messages: List[Dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_completion_tokens: int = 256,
    ) -> str:
        """Solicita una finalización de chat y devuelve el contenido del primer choice."""
        model = model or self.default_model

        """Solicita una finalización de chat y devuelve el contenido del primer choice.


        Reintenta ante errores transitorios hasta `self.max_retries`.
        Lanza `LLMResponseError` si la respuesta no contiene el formato esperado.
        """
        attempt = 0
        last_exc: Exception | None = None

        while attempt <= self.max_retries:
            try:
                logger.info(
                    "chat_completion: calling model=%r endpoint=%r api_version=%r",
                    model,
                    self.endpoint,
                    self.api_version,
                )
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_completion_tokens=max_completion_tokens,
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
                error_text = str(e)
                if "Resource not found" in error_text or "404" in error_text:
                    logger.exception(
                        "Azure OpenAI resource not found. Verifica endpoint y deployment/modelo.",
                        exc_info=e,
                    )
                    raise LLMConnectionError(
                        "Resource not found. Verifica que LLM_ENDPOINT y LLM_MODEL correspondan a una deployment válida."
                    ) from e

                logger.warning("Error en llamada LLM (intento %d): %s", attempt, e)

            # Exponencial backoff
            wait = min(2 ** attempt, 10)
            time.sleep(wait)
            attempt += 1

        raise LLMConnectionError(f"Fallo en llamadas LLM tras {self.max_retries} reintentos: {last_exc}")
