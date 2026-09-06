import unittest

from llama.llm_fields.location.decimalLatitude import DecimalLatitude


class TestDecimalLatitude(unittest.TestCase):
    def test_decimal_latitude_01(self) -> None:
        # A numeric string is parsed to a float
        assert DecimalLatitude("", "45.5").decimalLatitude == 45.5

    def test_decimal_latitude_02(self) -> None:
        # Negative values are preserved
        assert DecimalLatitude("", "-1.0").decimalLatitude == -1.0

    def test_decimal_latitude_03(self) -> None:
        # An integer string becomes a float
        assert DecimalLatitude("", "45").decimalLatitude == 45.0

    def test_decimal_latitude_04(self) -> None:
        # Direction letters are ignored
        assert DecimalLatitude("", "N45.5").decimalLatitude == 45.5
        assert DecimalLatitude("", "45.5 N").decimalLatitude == 45.5

    def test_decimal_latitude_05(self) -> None:
        # Unparseable values become an empty string
        assert DecimalLatitude("", "none").decimalLatitude == ""
        assert DecimalLatitude("", "").decimalLatitude == ""
        assert DecimalLatitude("", "not a number").decimalLatitude == ""

    def test_decimal_latitude_06(self) -> None:
        # Non-string values are handled
        assert DecimalLatitude("", 45).decimalLatitude == 45.0
        assert DecimalLatitude("", float("nan")).decimalLatitude == ""
        assert DecimalLatitude("", [45.5]).decimalLatitude == 45.5

    def test_decimal_latitude_10(self) -> None:
        # A malformed numeric string with several dots returns a blank string
        assert DecimalLatitude("", "45.6.7").decimalLatitude == ""

    def test_decimal_latitude_11(self) -> None:
        # It handles the European use of commas for the decimal point
        assert DecimalLatitude("", "45,5").decimalLatitude == 45.5
