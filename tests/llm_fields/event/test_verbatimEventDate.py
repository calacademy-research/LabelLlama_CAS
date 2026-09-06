import unittest

from llama.llm_fields.event.verbatimEventDate import VerbatimEventDate


class TestVerbatimEventDate(unittest.TestCase):
    def test_verbatim_event_date_01(self) -> None:
        # Already-ISO value passes through unchanged
        assert VerbatimEventDate("", "2024-05-25").verbatimEventDate == "2024-05-25"

    def test_verbatim_event_date_02(self) -> None:
        # Leading "Date:" label is removed
        assert (
            VerbatimEventDate("", "Date: 2024-05-25").verbatimEventDate == "2024-05-25"
        )

    def test_verbatim_event_date_03(self) -> None:
        # Label removal is case-insensitive and separator-agnostic
        assert (
            VerbatimEventDate("", "date 2024-05-25").verbatimEventDate == "2024-05-25"
        )

    def test_verbatim_event_date_04(self) -> None:
        # Empty inputs stay empty
        assert VerbatimEventDate("", "").verbatimEventDate == ""
        assert VerbatimEventDate("", "not present").verbatimEventDate == ""
        assert VerbatimEventDate("", "Date:").verbatimEventDate == ""

    def test_verbatim_event_date_11(self) -> None:
        # Do not edit date ranges
        assert (
            VerbatimEventDate("", "25 May 2024|30 May 2024").verbatimEventDate
            == "25 May 2024|30 May 2024"
        )

    def test_verbatim_event_date_12(self) -> None:
        # Expected: "1999" -> "1999" (Do not normalize dates)
        assert VerbatimEventDate("", "1999").verbatimEventDate == "1999"
