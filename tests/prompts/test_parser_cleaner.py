import inspect
import unittest
from pathlib import Path

from llama.calc_fields.event.eventDate import EventDate
from llama.calc_fields.location.locality import Locality
from llama.llm_fields.occurrence.associatedTaxa import AssociatedTaxa
from llama.llm_fields.taxon.scientificName import ScientificName
from llama.prompts.parser_cleaner import ParserCleaner
from llama.prompts.parser_prompt import ParserPrompt

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"
DIODE = PROMPTS_DIR / "diode_one_v1.md"


class TestParserCleaner(unittest.TestCase):
    def setUp(self) -> None:
        self.cleaner = ParserCleaner(DIODE)
        self.prompt = ParserPrompt(prompt=DIODE, model_id="model")

    def test_load_llm_field_classes_01(self) -> None:
        # The herbarium prompt lists 40 LLM fields; each name maps to class
        cleaner = ParserCleaner(PROMPTS_DIR / "herbarium_v2.md")

        assert len(cleaner.llm_field_classes) == 40
        assert cleaner.llm_field_classes["scientificName"] is ScientificName
        assert cleaner.llm_field_classes["associatedTaxa"] is AssociatedTaxa

    def test_load_calc_field_classes_02(self) -> None:
        # The herbarium prompt lists 9 calculated fields
        cleaner = ParserCleaner(PROMPTS_DIR / "herbarium_v2.md")

        assert len(cleaner.calc_field_classes) == 9
        assert cleaner.calc_field_classes["eventDate"] is EventDate
        assert cleaner.calc_field_classes["locality"] is Locality

    def test_field_classes_are_field_classes_03(self) -> None:
        # Every mapped value must be a real field class with field metadata
        cleaner = ParserCleaner(PROMPTS_DIR / "herbarium_v2.md")

        for classes in (
            cleaner.llm_field_classes,
            cleaner.calc_field_classes,
        ):
            for name, field_class in classes.items():
                with self.subTest(name=name):
                    assert inspect.isclass(field_class)
                    assert field_class.get_field_names()

    def test_validate_columns_ok_04(self) -> None:
        # A full set of prompt columns passes validation without error
        self.cleaner.validate_columns(list(self.prompt.columns), self.prompt)

    def test_validate_columns_missing_required_05(self) -> None:
        columns = [c for c in self.prompt.columns if c != "text"]

        with self.assertRaises(ValueError) as ctx:
            self.cleaner.validate_columns(columns, self.prompt)

        assert "text" in str(ctx.exception)

    def test_validate_columns_missing_prompt_column_06(self) -> None:
        columns = [c for c in self.prompt.columns if c != "habitat"]

        with self.assertRaises(ValueError) as ctx:
            self.cleaner.validate_columns(columns, self.prompt)

        assert "habitat" in str(ctx.exception)

    def test_get_llm_columns_07(self) -> None:
        # Only LLM field names are returned, in the dataframe's order
        df_columns = ["source", "habitat", "junk", "scientificName", "text"]

        assert self.cleaner.get_llm_columns(df_columns) == ["habitat", "scientificName"]

    def test_get_calc_columns_08(self) -> None:
        assert self.cleaner.get_calc_columns() == ["eventDate", "country", "locality"]

    def test_get_output_columns_09(self) -> None:
        columns = self.cleaner.get_output_columns()

        assert columns[:2] == ["source", "text"]
        assert "scientificName" in columns
        assert "eventDate" in columns
        # No column may appear twice
        assert len(columns) == len(set(columns))


if __name__ == "__main__":
    unittest.main()
