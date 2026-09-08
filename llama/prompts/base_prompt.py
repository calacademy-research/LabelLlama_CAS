import os
from enum import StrEnum
from typing import Any


class Thinking(StrEnum):
    USE_SERVER = "use server"
    DISABLE_TEMPLATE = "disable template"
    DISABLE_ARG = "disable arg"


class BasePrompt:
    def __init__(
        self,
        name: str = "",
        description: str = "",
        system_msg: str = "",
        base_headers: dict | None = None,
        base_payload: dict | None = None,
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.system_msg: str = system_msg
        self.base_headers: dict = base_headers or {}
        self.base_payload: dict = base_payload or {}

    def headers(self) -> dict:
        return self.base_headers

    def _headers(self) -> dict:
        head = {"Content-Type": "application/json"}
        api_key = os.getenv("LLM_API_KEY")
        if api_key:
            head["Authorization"] = f"Bearer {api_key}"
        return head

    def _payload_args(self, **kwargs: dict[str, Any]) -> dict:
        payload = {}
        if kwargs.get("temperature") is not None:
            payload["temperature"] = kwargs["temperature"]

        if kwargs.get("max_tokens") is not None:
            payload["max_tokens"] = kwargs["max_tokens"]

        match kwargs.get("thinking", Thinking.USE_SERVER):
            case Thinking.DISABLE_TEMPLATE:
                payload["chat_template_kwargs"] = {"enable_thinking": False}
            case Thinking.DISABLE_ARG:
                payload["enable_thinking"] = False
            case Thinking.USE_SERVER:
                pass
            case _:
                raise TypeError

        return payload
