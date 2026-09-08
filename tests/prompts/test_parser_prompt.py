import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from llama.llm_fields.taxon.scientificName import ScientificName
from llama.prompts.ocr_prompt import FIRST_COLUMNS
from llama.prompts.parser_prompt import ParserPrompt

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"
DIODE = PROMPTS_DIR / "diode_one_v1.md"


def make_stub_parser(
    llm_fields: list[object], req_fields: list[str] | None = None
) -> SimpleNamespace:
    return SimpleNamespace(
        name="stub",
        description="stub description",
        system_msg="You are a stub parser.",
        llm_fields=llm_fields,
        calc_fields=[],
        req_fields=req_fields or [],
    )


class TestParserPrompt(unittest.TestCase):
    def setUp(self) -> None:
        self.prompt = ParserPrompt(prompt=DIODE, model_id="model")

    def test_columns_01(self) -> None:
        # columns is the CSV header: reserved columns plus LLM field names
        assert self.prompt.columns[:4] == FIRST_COLUMNS
        assert "scientificName" in self.prompt.columns
        assert "occurrenceRemarks" in self.prompt.columns
        # Calc fields are not LLM columns
        assert "eventDate" not in self.prompt.columns

    def test_system_msg_has_field_guidance_and_schema_02(self) -> None:
        msg = self.prompt.system_msg

        assert "# Field Guidance" in msg
        assert "`scientificName`" in msg
        # The compressed JSON schema is appended to the message
        assert '"type": "json_schema"' in msg
        assert '"required": [ "scientificName" ]' in msg

    def test_json_schema_is_valid_json_03(self) -> None:
        obj = json.loads(self.prompt.json_schema)

        schema = obj["json_schema"]
        assert schema["name"] == "diode_one_v1"
        properties = schema["schema"]["properties"]
        assert list(properties) == self.prompt.columns[4:]
        assert all(v == {"type": "string"} for v in properties.values())
        assert schema["required"] == ["scientificName"]

    def test_base_payload_04(self) -> None:
        payload = self.prompt.base_payload

        assert payload["model"] == "model"
        assert payload["response_format"] == self.prompt.json_schema
        messages = payload["messages"]
        assert messages[0] == {"role": "system", "content": self.prompt.system_msg}
        assert messages[1] == {"role": "replace me"}

    def test_payload_builds_user_message_05(self) -> None:
        out = self.prompt.payload("some label text")

        assert out["model"] == "model"
        user_msg = out["messages"][-1]
        assert user_msg["role"] == "user"
        assert user_msg["content"] == (
            "Extract data from this `text`:\n\nsome label text"
        )
        # Repeated calls keep the placeholder in the base payload
        assert self.prompt.base_payload["messages"][-1] == {"role": "replace me"}

    def test_column_clash_06(self) -> None:
        assert ParserPrompt.column_clash(["text", "junk", "source"]) == [
            "text",
            "source",
        ]
        assert ParserPrompt.column_clash(["scientificName", "text"]) == ["text"]
        assert ParserPrompt.column_clash(["scientificName"]) == []

    def test_init_rejects_clashing_field_07(self) -> None:
        # An LLM field named after a reserved column must fail at load time
        stub = make_stub_parser([SimpleNamespace(name="text", field_class=None)])
        with (
            patch(
                "llama.prompts.parser_prompt.PromptFileParser",
                return_value=stub,
            ),
            self.assertRaises(ValueError) as ctx,
        ):
            ParserPrompt(prompt=DIODE, model_id="model")

        assert "text" in str(ctx.exception)

    def test_json_schema_without_required_fields_08(self) -> None:
        stub = make_stub_parser(
            [SimpleNamespace(name="scientificName", field_class=ScientificName)]
        )
        with patch(
            "llama.prompts.parser_prompt.PromptFileParser",
            return_value=stub,
        ):
            prompt = ParserPrompt(prompt=DIODE, model_id="model")

        obj = json.loads(prompt.json_schema)
        assert "required" not in obj["json_schema"]

    def test_parse_model_json_09(self) -> None:
        assert self.prompt.parse_model_json('```json\n{"a": "1"}\n```') == {"a": "1"}
        assert self.prompt.parse_model_json('{"a": "1"}') == {"a": "1"}

    def test_parse_model_json_rejects_non_object_10(self) -> None:
        with self.assertRaises(TypeError):
            self.prompt.parse_model_json("[1, 2]")
        with self.assertRaises(json.JSONDecodeError):
            self.prompt.parse_model_json("not json")


if __name__ == "__main__":
    unittest.main()
