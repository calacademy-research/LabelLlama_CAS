import inspect
import unittest
from dataclasses import dataclass, is_dataclass

from llama.llm_fields.llm_field import LlmField


@dataclass
class _SampleLlm(LlmField):
    """Minimal concrete subclass used to exercise the base class."""

    beta: str = ""


class TestLlmField(unittest.TestCase):
    def test_llm_field_01(self) -> None:
        # LlmField is a dataclass so subclasses can inherit from it
        assert is_dataclass(LlmField)

    def test_llm_field_02(self) -> None:
        # Subclasses construct as (text, **field_values)
        field = _SampleLlm("hello", "x")
        assert field.beta == "x"

    def test_llm_field_03(self) -> None:
        # text is the first init parameter (an InitVar)
        params = list(inspect.signature(LlmField).parameters)
        assert params[0] == "text"

    def test_llm_field_04(self) -> None:
        # get_field_names returns the (stored) field names of a subclass
        assert _SampleLlm.get_field_names() == ["beta"]

    def test_llm_field_05(self) -> None:
        # ClassVars (scoring_method) are not reported as fields
        assert "scoring_method" not in _SampleLlm.get_field_names()

    def test_llm_field_06(self) -> None:
        # Default scoring method
        assert LlmField.scoring_method == "LR"

    def test_llm_field_07(self) -> None:
        # score: identical values
        assert LlmField.score("abc", "abc", {}) == 1.0

    def test_llm_field_08(self) -> None:
        # score: surrounding whitespace is ignored
        assert LlmField.score(" abc ", "abc", {}) == 1.0

    def test_llm_field_09(self) -> None:
        # score: values are stringified before comparison
        assert LlmField.score(1.5, "1.5", {}) == 1.0

    def test_llm_field_10(self) -> None:
        # score: empty expect vs non-empty actual
        assert LlmField.score("", "abc", {}) == 0.0

    def test_llm_field_11(self) -> None:
        # InitVar fields (like text) are not part of the field list
        assert LlmField.get_field_names() == []


if __name__ == "__main__":
    unittest.main()
