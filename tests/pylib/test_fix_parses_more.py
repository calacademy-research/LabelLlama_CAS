import unittest

from llama.pylib.fix_parses import FixParses


class TestFixParsesMore(unittest.TestCase):
    def setUp(self) -> None:
        self.fp = FixParses()

    # ---------------------------------------------------------------------
    def test_date_to_iso_extra_01(self) -> None:
        # Roman-numeral month (viii = August)
        assert self.fp.date_to_iso("viii 1990") == "1990-08"

    def test_date_to_iso_extra_02(self) -> None:
        # A future date is shifted back 100 years
        assert self.fp.date_to_iso("2030-01-15") == "1930-01-15"

    def test_date_to_iso_extra_03(self) -> None:
        # Test a year-only date
        assert self.fp.date_to_iso("1990") == "1990"

    # ---------------------------------------------------------------------
    def test_title_with_exceptions_01(self) -> None:
        assert (
            FixParses.title_with_exceptions("the man and the woman")
            == "The Man and the Woman"
        )

    def test_title_with_exceptions_02(self) -> None:
        assert (
            FixParses.title_with_exceptions("river de la plata") == "River de La Plata"
        )

    # ---------------------------------------------------------------------
    def test_to_truthy_01(self) -> None:
        assert self.fp.to_truthy("yes") is True

    def test_to_truthy_02(self) -> None:
        # Falsy values yield "" rather than False
        assert self.fp.to_truthy("no") == ""

    def test_to_truthy_03(self) -> None:
        assert self.fp.to_truthy(1) is True

    def test_to_truthy_04(self) -> None:
        assert self.fp.to_truthy(0) == ""

    # ---------------------------------------------------------------------
    def test_reduce_list_01(self) -> None:
        assert self.fp.reduce_list([]) == []
        assert self.fp.reduce_list([1]) == 1
        assert self.fp.reduce_list([1, 2]) == [1, 2]

    def test_reduce_str_list_01(self) -> None:
        assert self.fp.reduce_str_list("") == ""
        assert self.fp.reduce_str_list(["a"]) == "a"

    def test_reduce_str_list_02(self) -> None:
        # multiple items are returned as a comma joined list
        assert self.fp.reduce_str_list(["a", "b"]) == "a, b"

    # ---------------------------------------------------------------------
    def test_to_int_extra_01(self) -> None:
        # The first integer is extracted from surrounding text
        assert self.fp.to_int("abc 12") == 12

    def test_to_int_extra_02(self) -> None:
        # The integer part is taken from a decimal string
        assert self.fp.to_int("1.5") == 1

    def test_to_int_extra_03(self) -> None:
        assert self.fp.to_int([5]) == 5
        assert self.fp.to_int([]) is None
        assert self.fp.to_int(None) is None

    # ---------------------------------------------------------------------
    def test_to_float_extra_01(self) -> None:
        assert self.fp.to_float(".5") == 0.5
        assert self.fp.to_float("abc 3.5") == 3.5
        assert self.fp.to_float(None) is None

    def test_to_float_extra_02(self) -> None:
        # Repeated dots are not a valid number
        assert self.fp.to_float("1.2.3") is None

    # ---------------------------------------------------------------------
    def test_to_bool_extra_01(self) -> None:
        assert self.fp.to_bool("on") is True
        assert self.fp.to_bool("off") is False

    # ---------------------------------------------------------------------
    def test_to_list_of_ints_extra_01(self) -> None:
        # A dashed range yields both values (no negative)
        assert self.fp.to_list_of_ints("12-34") == [12, 34]

    def test_to_list_of_floats_extra_01(self) -> None:
        assert self.fp.to_list_of_floats("1.5 2.5") == [1.5, 2.5]

    def test_to_list_of_floats_extra_02(self) -> None:
        # Reject malformed lists
        assert self.fp.to_list_of_floats("1.2.3") == []

    # ---------------------------------------------------------------------
    def test_str_to_float_extra_01(self) -> None:
        assert self.fp.str_to_float(".5") == 0.5
        assert self.fp.str_to_float("-2.5") == -2.5
        assert self.fp.str_to_float("abc") is None
        assert self.fp.str_to_float("1.2.3") is None

    def test_str_to_int_extra_01(self) -> None:
        assert self.fp.str_to_int("-5") == -5
        assert self.fp.str_to_int("abc") is None

    # ---------------------------------------------------------------------
    def test_stringified_list_extra_01(self) -> None:
        assert self.fp.stringified_list("['a', 'b']") == ["a", "b"]

    def test_stringified_list_extra_02(self) -> None:
        assert self.fp.stringified_list("not a list") == "not a list"

    # ---------------------------------------------------------------------
    def test_clean_str_extra_01(self) -> None:
        # Surrounding brackets of any kind are stripped
        assert self.fp.clean_str("(test)") == "test"
        assert self.fp.clean_str("[test]") == "test"
        assert self.fp.clean_str("{test}") == "test"

    def test_clean_str_extra_02(self) -> None:
        # Markdown bold / italic notations are removed
        assert self.fp.clean_str("**test**") == "test"
        assert self.fp.clean_str("_test_") == "test"

    def test_clean_str_extra_03(self) -> None:
        # Empty-field notations (case-insensitive) become ""
        assert self.fp.clean_str("NAN") == ""
        assert self.fp.clean_str("(blank)") == ""
        assert self.fp.clean_str("{none}") == ""
        assert self.fp.clean_str("[not specified]") == ""
        assert self.fp.clean_str("not present") == ""

    # ---------------------------------------------------------------------
    def test_to_str_extra_01(self) -> None:
        # Empty/cleaned-empty items are dropped when joining a list
        assert self.fp.to_str(["", "two"]) == "two"
        assert self.fp.to_str(None) == ""


if __name__ == "__main__":
    unittest.main()
