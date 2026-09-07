from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class StateProvince(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the state, province, or equivalent first-level administrative division
        where the specimen was collected.
        """
    # --------------

    stateProvince: str = ""

    def __post_init__(self, text: str) -> None:
        self.stateProvince = self.clean_punct(self.stateProvince)
        self.stateProvince = self.hallucinated_str(self.stateProvince, text)
        self.stateProvince = self.title_with_exceptions(self.stateProvince)
