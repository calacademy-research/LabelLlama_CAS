import inspect
import unittest
from dataclasses import dataclass, is_dataclass

from llama.calc_fields.calc_field import CalcField


@dataclass
class _SampleField(CalcField):
    """Minimal concrete subclass used to exercise the base class."""

    alpha: str = ""
    _hidden: str = ""


class TestCalcField(unittest.TestCase):
    def test_calc_field_01(self) -> None:
        # CalcField is a dataclass so subclasses can inherit from it
        assert is_dataclass(CalcField)

    def test_calc_field_02(self) -> None:
        # Subclasses construct as (cleaned_rec, **field_values)
        field = _SampleField({"a": 1}, "x")
        assert field.alpha == "x"

    def test_calc_field_03(self) -> None:
        # cleaned_rec is the first init parameter (an InitVar)
        params = list(inspect.signature(CalcField).parameters)
        assert params[0] == "cleaned_rec"

    def test_calc_field_04(self) -> None:
        # get_field_names returns the (stored) field names of a subclass
        assert _SampleField.get_field_names() == ["alpha", "_hidden"]

    def test_calc_field_05(self) -> None:
        # get_visible_fields excludes underscore-prefixed names
        assert _SampleField.get_visible_fields() == ["alpha"]

    def test_calc_field_06(self) -> None:
        # ClassVars (scoring_method) are not reported as fields
        assert "scoring_method" not in _SampleField.get_field_names()

    def test_calc_field_07(self) -> None:
        # Default scoring method
        assert CalcField.scoring_method == "LR"

    def test_calc_field_08(self) -> None:
        # score: identical values
        assert CalcField.score("abc", "abc", {}) == 1.0

    def test_calc_field_09(self) -> None:
        # score: surrounding whitespace is ignored
        assert CalcField.score(" abc ", "abc", {}) == 1.0

    def test_calc_field_10(self) -> None:
        # score: values are stringified before comparison
        assert CalcField.score(1.5, "1.5", {}) == 1.0

    def test_calc_field_11(self) -> None:
        # score: empty expect vs non-empty actual
        assert CalcField.score("", "abc", {}) == 0.0

    def test_calc_field_12(self) -> None:
        # score: similar but different values score in between
        assert 0.0 < CalcField.score("abc", "abd", {}) < 1.0

    def test_calc_field_13(self) -> None:
        # InitVar fields (like cleaned_rec) are not part of the field list
        assert CalcField.get_field_names() == []


if __name__ == "__main__":
    unittest.main()
