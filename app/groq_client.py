from typing import Any

from fastapi import HTTPException
from groq import Groq

from .config import settings


_client: Groq | None = None


def get_client() -> Groq:
    """
    Create one shared Groq client and reuse it.
    """

    global _client

    if _client is None:
        try:
            settings.validate()

            _client = Groq(
                api_key=settings.GROQ_API_KEY
            )

        except Exception as exc:
            print("Groq configuration error:")
            print(repr(exc))

            raise HTTPException(
                status_code=500,
                detail="Groq configuration error.",
            ) from exc

    return _client


def chat(
    messages: list[dict[str, Any]],
    temperature: float = 0.7,
    max_tokens: int = 800,
    model: str | None = None,
) -> str:
    """
    Send messages to Groq and return the generated response.
    """

    client = get_client()

    try:
        response = client.chat.completions.create(
            model=model or settings.GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if not response.choices:
            raise HTTPException(
                status_code=502,
                detail="Groq returned no response.",
            )

        content = response.choices[0].message.content

        return content or ""

    except Exception as exc:

        print("=" * 60)
        print("GROQ ERROR")
        print(repr(exc))
        print("=" * 60)

        error_text = str(exc)

        if "401" in error_text or "Invalid API Key" in error_text:
            raise HTTPException(
                status_code=502,
                detail="Groq authentication failed. Check GROQ_API_KEY.",
            ) from exc

        raise HTTPException(
            status_code=502,
            detail=f"Groq error: {error_text}",
        ) from exc


def chat_json(
    messages: list[dict[str, Any]],
    temperature: float = 0.4,
    max_tokens: int = 1200,
    model: str | None = None,
) -> str:
    """
    Same as chat(), but forces Groq to return valid JSON syntax (JSON mode).
    The system/user prompt still has to describe the exact shape you want -
    this only guarantees the string parses as JSON, not which fields it has.

    Pass `model` to override settings.GROQ_MODEL for this call — used for
    vision requests, which need a vision-capable model.
    """

    client = get_client()

    try:
        response = client.chat.completions.create(
            model=model or settings.GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        if not response.choices:
            raise HTTPException(
                status_code=502,
                detail="Groq returned no response.",
            )

        content = response.choices[0].message.content

        return content or "{}"

    except Exception as exc:

        print("=" * 60)
        print("GROQ ERROR (chat_json)")
        print(repr(exc))
        print("=" * 60)

        error_text = str(exc)

        if "401" in error_text or "Invalid API Key" in error_text:
            raise HTTPException(
                status_code=502,
                detail="Groq authentication failed. Check GROQ_API_KEY.",
            ) from exc

        raise HTTPException(
            status_code=502,
            detail=f"Groq error: {error_text}",
        ) from exc