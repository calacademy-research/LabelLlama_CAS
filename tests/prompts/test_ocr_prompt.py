import unittest
from pathlib import Path
from unittest.mock import patch

from llama.prompts.ocr_prompt import OcrPrompt

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


class TestOcrPrompt(unittest.TestCase):
    def test_columns_01(self) -> None:
        # columns is the CSV header used by ocr_images when writing results
        assert OcrPrompt.columns == ["status", "source", "elapsed", "text"]

    def test_load_ocr_v1_02(self) -> None:
        prompt = OcrPrompt(prompt=PROMPTS_DIR / "ocr_v1.md", model_id="model")

        assert prompt.name == "ocr"
        assert prompt.description == "OCR labels on images of museum specimens."
        # system_msg is the heading-less body of the "# System Message" section
        assert prompt.system_msg.startswith(
            "You are given an image of a museum specimen"
        )
        assert "hallucinate" in prompt.system_msg
        # Front matter and section headings are not part of the message
        assert "name:" not in prompt.system_msg
        assert "System Message" not in prompt.system_msg

    def test_load_ocr_v2_keeps_subsections_03(self) -> None:
        # "##" sub-headings inside the System Message must stay in system_msg
        prompt = OcrPrompt(prompt=PROMPTS_DIR / "ocr_v2.md", model_id="model")

        assert prompt.name == "ocr_v2"
        assert prompt.system_msg.startswith(
            "You will receive an image of a museum specimen"
        )
        assert "## What to Ignore" in prompt.system_msg
        assert "## Output Rules" in prompt.system_msg

    def test_default_instance_04(self) -> None:
        prompt = OcrPrompt(prompt=PROMPTS_DIR / "ocr_v2.md", model_id="model")

        assert prompt.name == "ocr_v2"
        assert prompt.description.startswith("OCR labels on images")

    def test_req_fields_empty_10(self) -> None:
        # TaskWriter.check() reads prompt.req_fields, so OcrPrompt must
        # define it (an OCR prompt has no required fields)
        prompt = OcrPrompt(prompt=PROMPTS_DIR / "ocr_v2.md", model_id="model")

        assert prompt.req_fields == []

    def test_base_payload_05(self) -> None:
        # base_payload has the model, a system message, and a placeholder
        prompt = OcrPrompt(prompt=PROMPTS_DIR / "ocr_v1.md", model_id="model")

        assert prompt.base_payload["model"] == "model"
        messages = prompt.base_payload["messages"]
        assert messages[0] == {"role": "system", "content": prompt.system_msg}
        assert messages[1] == {"role": "replace me"}

    def test_base_payload_extra_kwargs_06(self) -> None:
        # Sampling kwargs flow through to the payload
        prompt = OcrPrompt(
            prompt=PROMPTS_DIR / "ocr_v1.md",
            model_id="model",
            temperature=0.1,
            max_tokens=64,
        )

        assert prompt.base_payload["temperature"] == 0.1
        assert prompt.base_payload["max_tokens"] == 64

    def test_base_headers_07(self) -> None:

        env = {"LLM_API_KEY": "secret-key"}
        with patch.dict("os.environ", env, clear=True):
            prompt = OcrPrompt(prompt=PROMPTS_DIR / "ocr_v1.md", model_id="m")

        assert prompt.base_headers["Content-Type"] == "application/json"
        assert prompt.base_headers["Authorization"] == "Bearer secret-key"

    def test_payload_builds_user_message_08(self) -> None:
        prompt = OcrPrompt(prompt=PROMPTS_DIR / "ocr_v1.md", model_id="model")

        out = prompt.payload("image/jpeg", "aGVsbG8=")

        assert out["model"] == "model"
        user_msg = out["messages"][-1]
        assert user_msg["role"] == "user"
        assert user_msg["content"] == [
            {
                "type": "image_url",
                "image_url": {"url": "data:image/jpeg;base64,aGVsbG8="},
            }
        ]
        assert out["messages"][0]["role"] == "system"

    def test_payload_does_not_mutate_base_payload_09(self) -> None:
        # Repeated payload() calls must keep the placeholder intact
        prompt = OcrPrompt(prompt=PROMPTS_DIR / "ocr_v1.md", model_id="model")

        first = prompt.payload("image/png", "AAA")
        second = prompt.payload("image/png", "BBB")

        assert prompt.base_payload["messages"][-1] == {"role": "replace me"}
        assert first["messages"][-1] is not second["messages"][-1]


if __name__ == "__main__":
    unittest.main()
