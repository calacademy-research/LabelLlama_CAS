import unittest

from llama.llm_fields.location.decimalLongitude import DecimalLongitude


class TestDecimalLongitude(unittest.TestCase):
    def test_decimal_longitude_01(self) -> None:
        assert DecimalLongitude("", "-1.0").decimalLongitude == -1.0

    def test_decimal_longitude_02(self) -> None:
        # A numeric string is parsed to a float
        assert DecimalLongitude("", "-122.5").decimalLongitude == -122.5

    def test_decimal_longitude_03(self) -> None:
        # Direction letters are ignored
        assert DecimalLongitude("", "122.5 W").decimalLongitude == 122.5
        assert DecimalLongitude("", "W122.5").decimalLongitude == 122.5

    def test_decimal_longitude_04(self) -> None:
        # Unparseable values become an empty string
        assert DecimalLongitude("", "none").decimalLongitude == ""
        assert DecimalLongitude("", "").decimalLongitude == ""

    def test_decimal_longitude_05(self) -> None:
        # Non-string values are handled
        assert DecimalLongitude("", 45).decimalLongitude == 45.0
        assert DecimalLongitude("", float("nan")).decimalLongitude == ""
