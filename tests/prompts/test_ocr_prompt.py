import unittest
from pathlib import Path

from llama.prompts.ocr_prompt import OcrPrompt

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


class TestOcrPrompt(unittest.TestCase):
    def test_columns_01(self) -> None:
        # columns is the CSV header used by ocr_images when writing results
        assert OcrPrompt.columns == ["status", "source", "elapsed", "text"]

    def test_load_ocr_v1_02(self) -> None:
        prompt = OcrPrompt.load(PROMPTS_DIR / "ocr_v1.md")

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
        prompt = OcrPrompt.load(PROMPTS_DIR / "ocr_v2.md")

        assert prompt.name == "ocr_v2"
        assert prompt.system_msg.startswith(
            "You will receive an image of a museum specimen"
        )
        assert "## What to Ignore" in prompt.system_msg
        assert "## Output Rules" in prompt.system_msg

    def test_default_instance_04(self) -> None:
        prompt = OcrPrompt()

        assert prompt.name == ""
        assert prompt.description == ""
        assert prompt.system_msg == ""


if __name__ == "__main__":
    unittest.main()
