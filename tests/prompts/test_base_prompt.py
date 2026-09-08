import unittest
from unittest.mock import patch

from llama.prompts.base_prompt import Thinking, headers, payload_args


class TestBasePrompt(unittest.TestCase):
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

    def test_headers_without_api_key_07(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            assert headers() == {"Content-Type": "application/json"}

    def test_headers_with_api_key_08(self) -> None:
        env = {"LLM_API_KEY": "secret-key"}
        with patch.dict("os.environ", env, clear=True):
            head = headers()

        assert head["Content-Type"] == "application/json"
        assert head["Authorization"] == "Bearer secret-key"

    def test_no_kwargs_gives_empty_payload_09(self) -> None:
        assert payload_args() == {}

    def test_temperature_and_max_tokens_included_10(self) -> None:
        payload = payload_args(temperature=0.5, max_tokens=128)

        assert payload == {"temperature": 0.5, "max_tokens": 128}

    def test_none_values_are_omitted_11(self) -> None:
        payload = payload_args(temperature=None, max_tokens=None)

        assert payload == {}

    def test_zero_temperature_is_kept_12(self) -> None:
        # 0 is a valid temperature and must not be dropped like a falsy value
        payload = payload_args(temperature=0, max_tokens=0)

        assert payload == {"temperature": 0, "max_tokens": 0}

    def test_thinking_default_is_use_server_13(self) -> None:
        # No thinking kwarg -> no thinking-related payload keys at all
        assert payload_args() == {}

    def test_thinking_disable_template_14(self) -> None:
        payload = payload_args(thinking=Thinking.DISABLE_TEMPLATE)

        assert payload == {"chat_template_kwargs": {"enable_thinking": False}}

    def test_thinking_disable_arg_15(self) -> None:
        payload = payload_args(thinking=Thinking.DISABLE_ARG)

        assert payload == {"enable_thinking": False}

    def test_thinking_accepts_plain_strings_16(self) -> None:
        # Callers may pass the raw strings instead of Thinking members
        assert payload_args(thinking="use server") == {}
        assert payload_args(thinking="disable template") == {
            "chat_template_kwargs": {"enable_thinking": False}
        }
        assert payload_args(thinking="disable arg") == {"enable_thinking": False}

    def test_thinking_unknown_value_rejected_17(self) -> None:
        # An unrecognised thinking value must fail loudly
        with self.assertRaises(TypeError):
            payload_args(thinking="nonsense")

    def test_thinking_none_treated_as_unset_18(self) -> None:
        # Thinking is normalized
        assert payload_args(thinking=None) == {}


if __name__ == "__main__":
    unittest.main()
