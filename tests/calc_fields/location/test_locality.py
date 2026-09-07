import unittest

from llama.calc_fields.location.locality import Locality


class TestLocality(unittest.TestCase):
    def test_locality_01(self) -> None:
        actual = """UNITED STATES: Texas, Cameron . Pond near canal off CR 800"""
        expect = """Pond near canal off CR 800"""
        record = {
            "locality": actual,
            "country": "United States",
            "stateProvince": "Texas",
            "county": "Cameron",
        }
        assert Locality(record, actual).locality == expect

    def test_locality_02(self) -> None:
        actual = "UNITED STATES: Texas, Cameron County. Smith Ranch"
        expect = "Smith Ranch"
        record = {
            "locality": actual,
            "country": "United States",
            "stateProvince": "Texas",
            "county": "Cameron",
        }
        assert Locality(record, actual).locality == expect

    def test_locality_03(self) -> None:
        actual = "  double   spaces  "
        expect = "double spaces"
        assert Locality(None, actual).locality == expect

    def test_locality_04(self) -> None:
        # Remove county abbreviations
        actual = "Smith Co., some hill"
        expect = "Smith, some hill"
        assert Locality({}, actual).locality == expect
