import unittest
from pathlib import Path

from llama.calc_fields.event.eventDate import EventDate
from llama.calc_fields.location.elevation import Elevation
from llama.llm_fields.location.utm import Utm
from llama.llm_fields.taxon.scientificName import ScientificName
from llama.prompts.field_action import FieldAction


class TestFieldActionLoad(unittest.TestCase):
    def test_load_llm_field_01(self) -> None:
        # A standard "../llama/llm_fields/..." link loads the LLM field class
        action = FieldAction("../llama/llm_fields/location/utm.py")

        assert action.name == "utm"
        assert action.module == Path("../llama/llm_fields/location/utm.py")
        assert action.field_class is Utm
        assert action.columns == Utm.get_field_names() == ["utm"]

    def test_load_calc_field_02(self) -> None:
        # A standard "../llama/calc_fields/..." link loads the CalcField class
        action = FieldAction("../llama/calc_fields/event/eventDate.py")

        assert action.name == "eventDate"
        assert action.module == Path("../llama/calc_fields/event/eventDate.py")
        assert action.field_class is EventDate
        assert action.columns == EventDate.get_field_names() == ["eventDate"]

    def test_load_without_relative_prefix_03(self) -> None:
        # A link without the "../" prefix is imported the same way
        action = FieldAction("llama/llm_fields/location/utm.py")

        assert action.name == "utm"
        assert action.field_class is Utm

    def test_class_name_derived_from_file_stem_04(self) -> None:
        # camelCase file stem maps to the CamelCase class in that module
        action = FieldAction("../llama/llm_fields/taxon/scientificName.py")

        assert action.name == "scientificName"
        assert action.field_class is ScientificName
        assert action.columns == ["scientificName"]

    def test_loaded_fields_are_instantiable_05(self) -> None:
        # The classes loaded by FieldAction must be usable as field classes
        utm = FieldAction("../llama/llm_fields/location/utm.py")
        date = FieldAction("../llama/calc_fields/event/eventDate.py")

        assert utm.field_class("", "17N 500000 4500000").utm == "17N 500000 4500000"
        assert date.field_class().eventDate == ""

    def test_multi_column_calc_field_06(self) -> None:
        # A field class with several columns reports them all
        action = FieldAction("../llama/calc_fields/location/elevation.py")

        assert action.field_class is Elevation
        assert action.columns == Elevation.get_field_names()
        assert len(action.columns) > 1

    def test_missing_module_raises_07(self) -> None:
        # A link to a non-existent module fails loudly at construction
        with self.assertRaises(ModuleNotFoundError):
            FieldAction("../llama/llm_fields/location/nope.py")


if __name__ == "__main__":
    unittest.main()
