import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class VerbatimEventDate(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the date (or date range) when the specimen was collected or observed.
        Do not use the identification date.
        """
    # --------------

    verbatimEventDate: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.verbatimEventDate = self.to_str(self.verbatimEventDate)

        # Remove the date label
        self.verbatimEventDate = re.sub(
            r"\bdate\b[:,.;\s]*", "", self.verbatimEventDate, flags=re.IGNORECASE
        ).strip()
