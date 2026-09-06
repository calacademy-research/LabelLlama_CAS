import unittest

from llama.llm_fields.plants.flowerColor import FlowerColor


class TestFlowerColor(unittest.TestCase):
    def test_flower_color_01(self) -> None:
        # A value present in the text is kept
        assert FlowerColor("the flowers are red", "red").flowerColor == "red"

    def test_flower_color_02(self) -> None:
        # Matching is case-insensitive; the value keeps its own casing
        assert FlowerColor("the flowers are RED", "Red").flowerColor == "Red"

    def test_flower_color_03(self) -> None:
        # A value not present in the text is a hallucination and becomes empty
        assert FlowerColor("the flowers are white", "red").flowerColor == ""

    def test_flower_color_04(self) -> None:
        # An empty value stays empty
        assert FlowerColor("some text", "").flowerColor == ""

    def test_flower_color_05(self) -> None:
        # Trailing punctuation is removed once the value is matched in the text
        assert FlowerColor("the flowers are red.", "red.").flowerColor == "red"

    def test_flower_color_bug_01(self) -> None:
        # BUG (red): trailing punctuation is stripped AFTER the hallucination
        # check. The check searches for the literal value including its trailing
        # comma, so "red," is not found in "the flowers are red" and the whole
        # value is dropped to "" instead of being cleaned to "red".
        #
        # Suggested fix: remove the trailing punctuation BEFORE the
        # hallucination check:
        #     self.flowerColor = self.to_str(self.flowerColor)
        #     self.flowerColor = self.clean_punct(self.flowerColor)
        #     self.flowerColor = self.hallucinated_str(self.flowerColor, text)
        assert FlowerColor("the flowers are red", "red,").flowerColor == "red"

    def test_flower_color_bug_02(self) -> None:
        # BUG (red): same ordering flaw with a trailing period that the text
        # does not contain.
        assert FlowerColor("the flowers are red", "red.").flowerColor == "red"
