import tempfile
import unittest
from pathlib import Path

from llama.prompts.prompt_file_parser import PromptFileParser, get_front_yaml

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def write_prompt(text: str) -> Path:
    # Prompt files are parsed by path; use a temp file for synthetic ones
    tmp = tempfile.NamedTemporaryFile(
        "w", suffix=".md", delete=False, encoding="utf-8"
    )
    tmp.write(text)
    tmp.close()
    return Path(tmp.name)


class TestPromptFileParser(unittest.TestCase):
    def test_front_yaml_extraction_01(self) -> None:
        text = (
            "---\n"
            "name: ocr\n"
            "description: OCR labels.\n"
            "extra: 1\n"
            "---\n"
            "# System Message\n"
            "body\n"
        )

        front = get_front_yaml(text, Path("x.md"))

        assert front == {
            "name": "ocr",
            "description": "OCR labels.",
            "extra": 1,
        }

    def test_front_yaml_missing_raises_02(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            get_front_yaml("no front matter here", Path("x.md"))

        # The offending path is named in the error message
        assert "x.md" in str(ctx.exception)

    def test_front_yaml_unclosed_raises_03(self) -> None:
        with self.assertRaises(ValueError):
            get_front_yaml("---\nname: ocr\n", Path("x.md"))


    def test_ocr_v2_sections_04(self) -> None:
        parser = PromptFileParser(PROMPTS_DIR / "ocr_v2.md")

        assert parser.name == "ocr_v2"
        assert parser.description.startswith("OCR labels on images")
        # "##" sub-headings inside System Message must stay in system_msg
        assert parser.system_msg.startswith("You will receive an image")
        assert "## What to Ignore" in parser.system_msg
        assert "## Output Rules" in parser.system_msg
        # OCR prompts have no field sections; defaults stay empty
        assert parser.llm_fields == []
        assert parser.calc_fields == []
        assert parser.req_fields == []

    def test_diode_field_sections_05(self) -> None:
        parser = PromptFileParser(PROMPTS_DIR / "diode_one_v1.md")

        llm_names = [f.name for f in parser.llm_fields]
        assert len(llm_names) == 25
        assert llm_names[:2] == ["scientificName", "scientificNameAuthorship"]
        assert llm_names[-1] == "occurrenceRemarks"

        assert [f.name for f in parser.calc_fields] == [
            "eventDate",
            "country",
            "locality",
        ]
        assert parser.req_fields == ["scientificName"]

    def test_minimal_prompt_defaults_06(self) -> None:
        path = write_prompt(
            "---\nname: t\ndescription: d\n---\n"
            "# System Message\n"
            "The body.\n"
        )
        self.addCleanup(path.unlink, missing_ok=True)

        parser = PromptFileParser(path)

        assert parser.name == "t"
        assert parser.system_msg == "The body."
        assert parser.llm_fields == []
        assert parser.calc_fields == []
        assert parser.req_fields == []

    def test_sections_are_order_independent_07(self) -> None:
        # Required/Calculated before LLM Fields must parse the same way
        path = write_prompt(
            "---\nname: t\ndescription: d\n---\n"
            "# Required Fields\n"
            "- utm\n"
            "\n"
            "# Calculated Fields\n"
            "- [eventDate](../llama/calc_fields/event/eventDate.py)\n"
            "\n"
            "# LLM Fields\n"
            "- [utm](../llama/llm_fields/location/utm.py)\n"
            "\n"
            "# System Message\n"
            "The body.\n"
        )
        self.addCleanup(path.unlink, missing_ok=True)

        parser = PromptFileParser(path)

        assert [f.name for f in parser.llm_fields] == ["utm"]
        assert [f.name for f in parser.calc_fields] == ["eventDate"]
        assert parser.req_fields == ["utm"]
        assert parser.system_msg == "The body."

    def test_headings_are_case_insensitive_08(self) -> None:
        path = write_prompt(
            "---\nname: t\ndescription: d\n---\n"
            "# system message\n"
            "The body.\n"
        )
        self.addCleanup(path.unlink, missing_ok=True)

        assert PromptFileParser(path).system_msg == "The body."


if __name__ == "__main__":
    unittest.main()
