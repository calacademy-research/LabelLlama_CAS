import unittest

from llama.llm_fields.identification.identifiedByID import IdentifiedByID


class TestIdentifiedByID(unittest.TestCase):
    def test_identified_by_id_01(self) -> None:
        # Plain ID passes through unchanged
        assert IdentifiedByID("", "12345").identifiedByID == "12345"
        assert IdentifiedByID("", "GBIF:12345").identifiedByID == "GBIF:12345"

    def test_identified_by_id_02(self) -> None:
        # "No" label variations are removed
        assert IdentifiedByID("", "No. 12345").identifiedByID == "12345"
        assert IdentifiedByID("", "no 12345").identifiedByID == "12345"
        assert IdentifiedByID("", "Number: 12345").identifiedByID == "12345"
        assert IdentifiedByID("", "num 12345").identifiedByID == "12345"

    def test_identified_by_id_03(self) -> None:
        # Prefix markers are removed
        assert IdentifiedByID("", "#12345").identifiedByID == "12345"
        assert IdentifiedByID("", "Nº 12345").identifiedByID == "12345"

    def test_identified_by_id_04(self) -> None:
        # Empty inputs stay empty
        assert IdentifiedByID("", "").identifiedByID == ""
        assert IdentifiedByID("", "none").identifiedByID == ""

    def test_identified_by_id_05(self) -> None:
        # Lowercase ordinal without a space is removed
        assert IdentifiedByID("", "nº12345").identifiedByID == "12345"

    def test_identified_by_id_06(self) -> None:
        # Combined prefix markers and label+dot without space are removed
        assert IdentifiedByID("", "# Nº 12345").identifiedByID == "12345"
        assert IdentifiedByID("", "No.12345").identifiedByID == "12345"

    def test_identified_by_id_10(self) -> None:
        # Lowercase ordinal prefix is removed (case-insensitive)
        assert IdentifiedByID("", "nº 12345").identifiedByID == "12345"

    def test_identified_by_id_11(self) -> None:
        # Label followed by "#" then digits: both the label and the "#"
        # are removed ("#" has a word boundary after the label)
        assert IdentifiedByID("", "No#12345").identifiedByID == "12345"
        assert IdentifiedByID("", "number#12345").identifiedByID == "12345"

    def test_identified_by_id_12(self) -> None:
        # Label glued to the digits is removed
        assert IdentifiedByID("", "no12345").identifiedByID == "12345"

    def test_identified_by_id_13(self) -> None:
        # It handles the degree sign U+00B0 (a common way to type the ordinal)
        assert IdentifiedByID("", "N\u00b0 12345").identifiedByID == "12345"

    def test_identified_by_id_14(self) -> None:
        # It only handles the given labels
        # "renumber 12345" -> "renumber 12345"
        assert IdentifiedByID("", "non-12345").identifiedByID == "non-12345"
        assert IdentifiedByID("", "renumber 12345").identifiedByID == "renumber 12345"
