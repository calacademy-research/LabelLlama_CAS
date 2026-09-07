import unittest

from llama.calc_fields.event.eventDate import EventDate


class TestEventDate(unittest.TestCase):
    def test_event_date_01(self) -> None:
        record = {"verbatimEventDate": "1990-05-01"}
        assert EventDate(record, "").eventDate == "1990-05-01"

    def test_event_date_02(self) -> None:
        record = {"verbatimEventDate": "May 1990"}
        assert EventDate(record, "").eventDate == "1990-05"

    def test_event_date_03(self) -> None:
        record = {"verbatimEventDate": "1990-05-01|1990-05-03"}
        assert EventDate(record, "").eventDate == "1990-05-01 to 1990-05-03"

    def test_event_date_04(self) -> None:
        record = {"verbatimEventDate": "May 1990 | June 1990"}
        assert EventDate(record, "").eventDate == "1990-05 to 1990-06"

    def test_event_date_05(self) -> None:
        record = {"verbatimEventDate": ""}
        assert EventDate(record, "").eventDate == ""

    def test_event_date_06(self) -> None:
        assert EventDate({}, "").eventDate == ""

    def test_event_date_07(self) -> None:
        record = {"verbatimEventDate": None}
        assert EventDate(record, "").eventDate == ""

    def test_event_date_08(self) -> None:
        record = {"verbatimEventDate": float("nan")}
        assert EventDate(record, "").eventDate == ""

    def test_event_date_09(self) -> None:
        # Remove invalid dates from a date range
        record = {"verbatimEventDate": "1990-05-01|not a date"}
        assert EventDate(record, "").eventDate == "1990-05-01"

    def test_event_date_10(self) -> None:
        # Remove invalid dates from a date range
        record = {"verbatimEventDate": "n/a|1990-05-03"}
        assert EventDate(record, "").eventDate == "1990-05-03"

    def test_event_date_11(self) -> None:
        # Remove invalid dates from a date range
        record = {"verbatimEventDate": "n/a|also n/a"}
        assert EventDate(record, "").eventDate == ""


if __name__ == "__main__":
    unittest.main()
