import unittest

from llama.calc_fields.location.country import Country


class TestCountry(unittest.TestCase):
    def test_country_01(self) -> None:
        rec = {"stateProvince": "Texas"}
        assert Country(rec, "").country == "United States"

    def test_country_02(self) -> None:
        rec = {"county": "Kitsap"}
        assert Country(rec, "").country == "United States"

    def test_country_03(self) -> None:
        rec = {"stateProvince": "Ontario"}
        assert Country(rec, "").country == ""

    def test_country_04(self) -> None:
        rec = {"county": "Kildare"}
        assert Country(rec, "").country == ""

    def test_country_05(self) -> None:
        assert Country({"stateProvince": "Texas"}, "Canada").country == "Canada"

    def test_country_06(self) -> None:
        assert Country({}, "usa").country == "USA"

    def test_country_07(self) -> None:
        # Test the lookup lowers text before a search
        assert Country({}, "U.S.A.").country == "USA"


if __name__ == "__main__":
    unittest.main()
