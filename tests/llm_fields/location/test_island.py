import unittest

from llama.llm_fields.location.island import Island


class TestIsland(unittest.TestCase):
    def test_island_01(self) -> None:
        # Value present in the text is kept (case-insensitive)
        assert Island("on long island", "Long Island").island == "Long Island"

    def test_island_02(self) -> None:
        # Value not present in the text is a hallucination and becomes empty
        assert Island("on the mainland", "Long Island").island == ""

    def test_island_03(self) -> None:
        # Empty text: everything is a hallucination
        assert Island("", "Long Island").island == ""
