import unittest
from pathlib import Path
from types import SimpleNamespace

from llama.prompts.text_cleaner import (
    REQUIRED_PARSED_COLUMNS,
    TextCleaner,
)

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"
DIODE = PROMPTS_DIR / "diode_one_v1.md"


def make_cleaner() -> TextCleaner:
    return TextCleaner(DIODE)


class TestTextCleaner(unittest.TestCase):
    def test_init_field_classes_01(self) -> None:
        cleaner = make_cleaner()

        self.assertEqual(len(cleaner.llm_field_classes), 25)
        self.assertIn("scientificName", cleaner.llm_field_classes)
        self.assertEqual(
            list(cleaner.calc_field_classes),
            ["eventDate", "country", "locality"],
        )

    def test_validate_columns_ok_02(self) -> None:
        cleaner = make_cleaner()
        prompt = SimpleNamespace(
            columns=["status", "source", "elapsed", "text", "scientificName"]
        )

        # Should not raise when all required and prompt columns are present
        self.assertIsNone(cleaner.validate_columns(list(prompt.columns), prompt))

    def test_validate_columns_missing_required_03(self) -> None:
        cleaner = make_cleaner()
        prompt = SimpleNamespace(columns=[*REQUIRED_PARSED_COLUMNS, "scientificName"])

        with self.assertRaises(ValueError) as ctx:
            cleaner.validate_columns(["status", "source"], prompt)

        msg = str(ctx.exception)
        self.assertIn("required", msg)
        self.assertIn("text", msg)

    def test_validate_columns_missing_prompt_columns_04(self) -> None:
        cleaner = make_cleaner()
        prompt = SimpleNamespace(
            columns=["status", "source", "elapsed", "text", "scientificName"]
        )

        with self.assertRaises(ValueError) as ctx:
            cleaner.validate_columns(["status", "source", "elapsed", "text"], prompt)

        msg = str(ctx.exception)
        self.assertIn("prompt columns", msg)
        self.assertIn("scientificName", msg)

    def test_get_llm_columns_05(self) -> None:
        cleaner = make_cleaner()

        columns = [
            "status",
            "source",
            "catalogNumber",
            "scientificName",
            "extra",
        ]
        self.assertEqual(
            cleaner.get_llm_columns(columns),
            ["catalogNumber", "scientificName"],
        )

    def test_get_calc_columns_06(self) -> None:
        cleaner = make_cleaner()

        self.assertEqual(
            cleaner.get_calc_columns(), ["eventDate", "country", "locality"]
        )

    def test_get_output_columns_07(self) -> None:
        cleaner = make_cleaner()
        columns = cleaner.get_output_columns()

        self.assertEqual(columns[:2], ["source", "text"])
        self.assertIn("scientificName", columns)
        self.assertIn("eventDate", columns)
        # No duplicates, and no parse-only columns leak in
        self.assertEqual(len(columns), len(set(columns)))
        self.assertNotIn("status", columns)
        self.assertNotIn("elapsed", columns)


if __name__ == "__main__":
    unittest.main()
