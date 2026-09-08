import unittest
from unittest.mock import patch

from llama.prompts.base_prompt import BasePrompt, Thinking


class TestThinking(unittest.TestCase):
    def test_values_are_plain_strings_01(self) -> None:
        # Thinking is a StrEnum, so members compare and work as plain strings
        assert isinstance(Thinking.USE_SERVER, str)
        assert Thinking("use server") is Thinking.USE_SERVER
        assert Thinking("disable template") is Thinking.DISABLE_TEMPLATE
        assert Thinking("disable arg") is Thinking.DISABLE_ARG

    def test_equality_with_plain_strings_02(self) -> None:
        assert Thinking.USE_SERVER == "use server"
        assert Thinking.DISABLE_TEMPLATE == "disable template"
        assert Thinking.DISABLE_ARG == "disable arg"


class TestBasePromptDefaults(unittest.TestCase):
    def test_field_defaults_01(self) -> None:
        prompt = BasePrompt()

        assert prompt.name == ""
        assert prompt.description == ""
        assert prompt.system_msg == ""
        assert prompt.base_headers == {}
        assert prompt.base_payload == {}

    def test_dict_defaults_are_independent_per_instance_02(self) -> None:
        # base_headers / base_payload must not be shared between instances
        first = BasePrompt()
        second = BasePrompt()

        first.base_headers["Content-Type"] = "application/json"
        first.base_payload["model"] = "some-model"

        assert second.base_headers == {}
        assert second.base_payload == {}


class TestHeaders(unittest.TestCase):
    def test_headers_returns_base_headers_01(self) -> None:
        prompt = BasePrompt(base_headers={"X-Custom": "1"})

        assert prompt.headers() == {"X-Custom": "1"}

    def test_headers_without_api_key_02(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            assert BasePrompt()._headers() == {"Content-Type": "application/json"}

    def test_headers_with_api_key_03(self) -> None:
        env = {"LLM_API_KEY": "secret-key"}
        with patch.dict("os.environ", env, clear=True):
            head = BasePrompt()._headers()

        assert head["Content-Type"] == "application/json"
        assert head["Authorization"] == "Bearer secret-key"


class TestPayloadArgs(unittest.TestCase):
    def test_no_kwargs_gives_empty_payload_01(self) -> None:
        assert BasePrompt()._payload_args() == {}

    def test_temperature_and_max_tokens_included_02(self) -> None:
        payload = BasePrompt()._payload_args(temperature=0.5, max_tokens=128)

        assert payload == {"temperature": 0.5, "max_tokens": 128}

    def test_none_values_are_omitted_03(self) -> None:
        payload = BasePrompt()._payload_args(temperature=None, max_tokens=None)

        assert payload == {}

    def test_zero_temperature_is_kept_04(self) -> None:
        # 0 is a valid temperature and must not be dropped like a falsy value
        payload = BasePrompt()._payload_args(temperature=0, max_tokens=0)

        assert payload == {"temperature": 0, "max_tokens": 0}

    def test_thinking_default_is_use_server_05(self) -> None:
        # No thinking kwarg -> no thinking-related payload keys at all
        assert BasePrompt()._payload_args() == {}

    def test_thinking_disable_template_06(self) -> None:
        payload = BasePrompt()._payload_args(thinking=Thinking.DISABLE_TEMPLATE)

        assert payload == {"chat_template_kwargs": {"enable_thinking": False}}

    def test_thinking_disable_arg_07(self) -> None:
        payload = BasePrompt()._payload_args(thinking=Thinking.DISABLE_ARG)

        assert payload == {"enable_thinking": False}

    def test_thinking_accepts_plain_strings_08(self) -> None:
        # Callers may pass the raw strings instead of Thinking members
        assert BasePrompt()._payload_args(thinking="use server") == {}
        assert BasePrompt()._payload_args(thinking="disable template") == {
            "chat_template_kwargs": {"enable_thinking": False}
        }
        assert BasePrompt()._payload_args(thinking="disable arg") == {
            "enable_thinking": False
        }

    def test_thinking_unknown_value_rejected_09(self) -> None:
        # RED: an unrecognised thinking value is silently ignored by the
        # match statement instead of failing loudly.
        # Suggested fix: add a `case _:` branch in _payload_args that raises
        # ValueError (or TypeError) for unknown thinking values.
        with self.assertRaises((ValueError, TypeError)):
            BasePrompt()._payload_args(thinking="nonsense")


if __name__ == "__main__":
    unittest.main()
