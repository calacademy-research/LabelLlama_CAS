import os
from enum import StrEnum
from typing import Any


class Thinking(StrEnum):
    USE_SERVER = "use server"
    DISABLE_TEMPLATE = "disable template"
    DISABLE_ARG = "disable arg"


def headers() -> dict:
    head = {"Content-Type": "application/json"}
    api_key = os.getenv("LLM_API_KEY")
    if api_key:
        head["Authorization"] = f"Bearer {api_key}"
    return head


def payload_args(**kwargs: dict[str, Any]) -> dict:
    payload = {}
    if kwargs.get("temperature") is not None:
        payload["temperature"] = kwargs["temperature"]

    if kwargs.get("max_tokens") is not None:
        payload["max_tokens"] = kwargs["max_tokens"]

    thinking = kwargs.get("thinking") or Thinking.USE_SERVER
    match thinking:
        case Thinking.DISABLE_TEMPLATE:
            payload["chat_template_kwargs"] = {"enable_thinking": False}
        case Thinking.DISABLE_ARG:
            payload["enable_thinking"] = False
        case Thinking.USE_SERVER:
            pass
        case _:
            raise TypeError

    return payload
