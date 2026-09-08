import inspect
import unittest
from pathlib import Path

from llama.calc_fields.event.eventDate import EventDate
from llama.calc_fields.location.locality import Locality
from llama.llm_fields.occurrence.associatedTaxa import AssociatedTaxa
from llama.llm_fields.taxon.scientificName import ScientificName
from llama.prompts.parser_cleaner import ParserCleaner

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


class TestParserCleaner(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
