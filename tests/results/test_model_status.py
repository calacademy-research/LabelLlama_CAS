import unittest

from llama.results.model_status import ModelStatus, StatusCounts


class TestModelStatus(unittest.TestCase):
    def test_enum_values_01(self) -> None:
        # SUCCESS and UNKNOWN values are compared directly against CSV
        # strings elsewhere in the codebase, so they must stay exact
        assert ModelStatus.SUCCESS == "success"
        assert ModelStatus.UNKNOWN == ""
        assert len(ModelStatus) == 3

    def test_normalize_success_variants_02(self) -> None:
        for value in ("success", "SUCCESS", " Success ", "sUcCeSs"):
            with self.subTest(value=value):
                assert ModelStatus.normalize(value) is ModelStatus.SUCCESS

    def test_normalize_error_variants_03(self) -> None:
        for value in ("error", "ERROR", " Error "):
            with self.subTest(value=value):
                assert ModelStatus.normalize(value) is ModelStatus.ERROR

    def test_normalize_unknown_values_04(self) -> None:
        for value in ("", None, "   ", "failed", "timeout", 5):
            with self.subTest(value=value):
                assert ModelStatus.normalize(value) is ModelStatus.UNKNOWN

    def test_normalize_accepts_enum_members_05(self) -> None:
        assert ModelStatus.normalize(ModelStatus.SUCCESS) is ModelStatus.SUCCESS
        assert ModelStatus.normalize(ModelStatus.ERROR) is ModelStatus.ERROR
        assert ModelStatus.normalize(ModelStatus.UNKNOWN) is ModelStatus.UNKNOWN

    def test_is_success_06(self) -> None:
        assert ModelStatus.is_success("success")
        assert ModelStatus.is_success("SUCCESS")
        assert ModelStatus.is_success(ModelStatus.SUCCESS)
        assert not ModelStatus.is_success("error")
        assert not ModelStatus.is_success("")
        assert not ModelStatus.is_success(None)

    def test_count_normalizes_and_increments_07(self) -> None:
        counts = StatusCounts()

        assert counts.count("success") is ModelStatus.SUCCESS
        assert counts.count("SUCCESS ") is ModelStatus.SUCCESS
        assert counts.count("ERROR") is ModelStatus.ERROR
        assert counts.count("junk") is ModelStatus.UNKNOWN

        assert counts.get(ModelStatus.SUCCESS) == 2
        assert counts.get(ModelStatus.ERROR) == 1
        assert counts.get(ModelStatus.UNKNOWN) == 1

    def test_get_default_for_missing_08(self) -> None:
        counts = StatusCounts()

        assert counts.get(ModelStatus.SUCCESS) == 0
        assert counts.get(ModelStatus.SUCCESS, default=7) == 7

        counts.count("success")
        assert counts.get(ModelStatus.SUCCESS, default=7) == 1

    def test_getitem_09(self) -> None:
        counts = StatusCounts()

        # Unseen statuses read as 0 (no KeyError)
        assert counts[ModelStatus.ERROR] == 0

        counts.count("error")
        counts.count(" Error ")
        assert counts[ModelStatus.ERROR] == 2


if __name__ == "__main__":
    unittest.main()
