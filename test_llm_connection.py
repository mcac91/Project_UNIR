"""
test_llm_connection.py

Script de prueba para validar conexión con proveedor LLM.
Valida:
  - Carga de variables de entorno
  - Conexión al modelo LLM
  - Respuesta correcta de prueba simple

Uso: python test_llm_connection.py
"""

import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_environment() -> dict[str, str]:
    """Carga variables de entorno desde .env."""
    env_path = Path(".env")
    
    if not env_path.exists():
        logger.error("❌ Archivo .env no encontrado.")
        logger.info("   Copia .env.example a .env y rellena con tus valores:")
        logger.info("   - LLM_PROVIDER (azure_openai, openai, etc.)")
        logger.info("   - LLM_API_KEY")
        logger.info("   - LLM_ENDPOINT (si es Azure)")
        logger.info("   - LLM_MODEL")
        sys.exit(1)
    
    load_dotenv(env_path)
    logger.info("✅ Archivo .env cargado")
    
    # Validar variables requeridas
    required_vars = [
        "LLM_PROVIDER",
        "LLM_API_KEY",
        "LLM_MODEL"
    ]
    
    env_dict = {}
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            logger.error(f"❌ Variable requerida {var} no está configurada")
            sys.exit(1)
        env_dict[var] = value
    
    # Variables opcionales
    env_dict["LLM_ENDPOINT"] = os.getenv("LLM_ENDPOINT", "")
    env_dict["LLM_API_VERSION"] = os.getenv("LLM_API_VERSION", "2024-10-21")
    env_dict["LLM_TIMEOUT"] = int(os.getenv("LLM_TIMEOUT", "30"))
    env_dict["LLM_MAX_RETRIES"] = int(os.getenv("LLM_MAX_RETRIES", "3"))
    
    logger.info("✅ Variables de entorno validadas")
    return env_dict


def test_openai_connection(env: dict[str, str]) -> bool:
    """Prueba conexión con OpenAI y Azure OpenAI usando la librería oficial."""
    try:
        from openai import OpenAI

        provider = env["LLM_PROVIDER"].lower()
        logger.info(f"🔄 Conectando con proveedor LLM: {provider}")

        if provider == "azure_openai":
            if not env.get("LLM_ENDPOINT"):
                logger.error("❌ LLM_ENDPOINT requerido para Azure OpenAI")
                return False

                                    # En Azure OpenAI, el campo `model` de las llamadas suele ser el *deployment name*.
            # Además, el endpoint debe incluir el esquema y el dominio del recurso.

            endpoint = env["LLM_ENDPOINT"].strip()
            if not endpoint.startswith("http"):
                logger.warning(
                    "⚠️ LLM_ENDPOINT no parece incluir esquema (http/https). "
                    "Verifica que sea del tipo https://<recurso>.openai.azure.com/."
                )

                        # Compatibilidad con distintas versiones del SDK `openai`.
            # Si la versión no soporta `api_version` en el constructor, lo pasamos en la query del base_url.
            api_version = env["LLM_API_VERSION"].strip()

            try:
                # Algunas versiones soportan AzureOpenAI con api_version en el constructor.
                from openai import AzureOpenAI

                client = AzureOpenAI(
                    api_key=env["LLM_API_KEY"],
                    azure_endpoint=endpoint,
                    api_version=api_version,
                )
            except Exception:
                # Fallback: incluir api-version en base_url y usar OpenAI.
                sep = "&" if "?" in endpoint else "?"
                base_url = f"{endpoint}{sep}api-version={api_version}"
                client = OpenAI(api_key=env["LLM_API_KEY"], base_url=base_url)
        else:
            client = OpenAI(api_key=env["LLM_API_KEY"])

        logger.info("✅ Cliente OpenAI inicializado")

        # Prueba simple
        logger.info("🔄 Enviando prueba al modelo...")
                # Para Azure OpenAI, `env["LLM_MODEL"]` debería ser el *deployment name*.
        model = env["LLM_MODEL"].strip()
        if provider == "azure_openai":
            logger.info(f"🧩 (Azure) Usando deployment/model: {model}")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "Responde con una palabra: TEST"
                }
            ],
            temperature=0.7,
            max_completion_tokens=10,
        )

        content = response.choices[0].message.content
        logger.info(f"✅ Respuesta del modelo: {content}")
        return True

    except ImportError:
        logger.error("❌ openai no instalado. Ejecuta: pip install openai")
        return False
    except Exception as e:
        # Mensajes comunes:
        # - Missing credentials: api_key no llega o no se configura correctamente.
        # - Resource not found / incorrect model: deployment/model no coincide.
        logger.error(f"❌ Error en conexión OpenAI: {e}")
        if provider == "azure_openai":
            logger.info(
                "ℹ️ Revisa: LLM_API_KEY, LLM_ENDPOINT y que LLM_MODEL sea el *deployment name* "
                "creado en Azure OpenAI."
            )
        return False


def main() -> None:
    """Función principal."""
    logger.info("=" * 60)
    logger.info("TEST DE CONEXIÓN LLM")
    logger.info("=" * 60)

    # Paso 1: Cargar entorno
    env = load_environment()

    # Paso 2: Seleccionar proveedor y conectar
    success = test_openai_connection(env)

    # Resultado final
    logger.info("=" * 60)
    if success:
        logger.info("✅ PRUEBA EXITOSA: Conexión LLM funciona correctamente")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("❌ PRUEBA FALLIDA: Revisa los errores anteriores")
        logger.info("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
