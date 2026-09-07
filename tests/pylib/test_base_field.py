import unittest

from llama.pylib.base_field import BaseField


class TestBaseField(unittest.TestCase):
    def test_base_field_01(self) -> None:
        # The base class has no fields of its own and instantiates directly
        assert BaseField() is not None

    def test_base_field_02(self) -> None:
        assert BaseField.get_field_names() == []

    def test_base_field_03(self) -> None:
        assert BaseField.get_visible_fields() == []

    def test_base_field_04(self) -> None:
        # score: both values empty
        assert BaseField.score("", "", {}) == 1.0

    def test_base_field_05(self) -> None:
        # score: the record argument is ignored
        assert BaseField.score("abc", "abcx", {"a": 1}) == BaseField.score(
            "abc", "abcx", {}
        )


if __name__ == "__main__":
    unittest.main()
