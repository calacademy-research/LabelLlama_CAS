import unittest

from llama.calc_fields.location.elevation import Elevation


def make_elevation(verbatim: str) -> Elevation:
    return Elevation({"verbatimElevation": verbatim}, "")


class TestElevation(unittest.TestCase):
    def test_elevation_01(self) -> None:
        e = make_elevation("100 m")
        assert e.elevation == 100.0
        assert e.minimumElevationInMeters == 100.0
        assert e.maximumElevationInMeters == ""
        assert e.elevationUnits == "m"
        assert e.elevationEstimated is False

    def test_elevation_02(self) -> None:
        e = make_elevation("3000 ft")
        assert e.elevation == 3000.0
        self.assertAlmostEqual(e.minimumElevationInMeters, 914.4)
        assert e.maximumElevationInMeters == ""
        assert e.elevationUnits == "ft"

    def test_elevation_03(self) -> None:
        assert make_elevation("about 100 m").elevationEstimated is True
        assert make_elevation("100 m").elevationEstimated is False

    def test_elevation_04(self) -> None:
        e = make_elevation("100 m 1000 ft")
        assert e.minimumElevationInMeters == 100.0
        assert e.maximumElevationInMeters == ""
        assert e.elevationUnits == "m"

    def test_elevation_05(self) -> None:
        e = make_elevation("100")
        assert e.elevation == ""
        assert e.minimumElevationInMeters == ""
        assert e.maximumElevationInMeters == ""
        assert e.elevationUnits == ""
        assert e.elevationEstimated == ""

    def test_elevation_06(self) -> None:
        e = make_elevation("")
        assert e.elevation == ""
        assert e.elevationUnits == ""

    def test_elevation_07(self) -> None:
        # It handles an elevation range
        e = make_elevation("100-200 m")
        assert e.elevation == 100.0
        assert e.minimumElevationInMeters == 100.0
        assert e.maximumElevationInMeters == 200.0

    def test_elevation_08(self) -> None:
        # Meters must come after miles in the vocab/terms/unit_terms.csv
        e = make_elevation("100 mi")
        self.assertAlmostEqual(e.minimumElevationInMeters, 160934.4)
        assert e.elevationUnits == "mi"

    def test_elevation_09(self) -> None:
        # BUG: same root cause as test_elevation_08: "mm" is
        # parsed as "m", so 100 mm is reported as 100 meters instead of 0.1.
        # Same suggested fix (sort patterns longest first in units.py).
        e = make_elevation("100 mm")
        self.assertAlmostEqual(e.minimumElevationInMeters, 0.1)
        assert e.elevationUnits == "mm"


if __name__ == "__main__":
    unittest.main()
