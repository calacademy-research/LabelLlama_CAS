import unittest

from llama.llm_fields.location.country import Country


class TestCountry(unittest.TestCase):
    def test_country_01(self) -> None:
        # Values are title-cased
        assert Country("", "united states").country == "United States"

    def test_country_02(self) -> None:
        # Small words are lowercased except at the start
        assert Country("", "island of man").country == "Island of Man"
        assert Country("", "the netherlands").country == "The Netherlands"

    def test_country_03(self) -> None:
        # Already-cased values are unchanged
        assert Country("", "United States").country == "United States"

    def test_country_04(self) -> None:
        # Empty input stays empty
        assert Country("", "").country == ""

    def test_country_10(self) -> None:
        # attribute 'title'. Expected: None -> ""
        assert Country("", None).country == ""

    def test_country_11(self) -> None:
        # "none" -> ""
        assert Country("", "none").country == ""

    def test_country_12(self) -> None:
        # "st. john's" -> "St. John's"
        assert Country("", "st. john's").country == "St. John's"
