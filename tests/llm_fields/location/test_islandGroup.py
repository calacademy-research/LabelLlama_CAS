import unittest

from llama.llm_fields.location.islandGroup import IslandGroup


class TestIslandGroup(unittest.TestCase):
    def test_island_group_01(self) -> None:
        # Value present in the text is kept (case-insensitive)
        assert (
            IslandGroup("in the Hawaiian Islands", "Hawaiian Islands").islandGroup
            == "Hawaiian Islands"
        )

    def test_island_group_02(self) -> None:
        # Value not present in the text is a hallucination and becomes empty
        assert IslandGroup("on the mainland", "Hawaiian Islands").islandGroup == ""

    def test_island_group_03(self) -> None:
        # Empty text: everything is a hallucination
        assert IslandGroup("", "Hawaiian Islands").islandGroup == ""
