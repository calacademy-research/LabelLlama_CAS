from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from llama.prompts.prompt_file_parser import PromptFileParser

if TYPE_CHECKING:
    from pathlib import Path

    from llama.prompts.parser_prompt import ParserPrompt

REQUIRED_PARSED_COLUMNS = {"status", "source", "text"}


@dataclass
class ParserCleaner:
    llm_field_classes: dict[str, Any] = field(default_factory=dict[str, Any])
    calc_field_classes: dict[str, Any] = field(default_factory=dict[str, Any])

    @classmethod
    def load(cls, prompt_path: Path) -> ParserCleaner:
        prompt_parser = PromptFileParser.load(prompt_path)
        cleaner = cls(
            llm_field_classes={f.name: f.field_class for f in prompt_parser.llm_fields},
            calc_field_classes={
                f.name: f.field_class for f in prompt_parser.calc_fields
            },
        )
        return cleaner

    def validate_columns(self, df_columns: list[str], prompt: ParserPrompt) -> None:
        missing_required = REQUIRED_PARSED_COLUMNS - set(df_columns)
        if missing_required:
            missing = ", ".join(sorted(missing_required))
            raise ValueError(f"Parsed file is missing required columns: {missing}")

        missing_expected = set(prompt.columns) - set(df_columns)
        if missing_expected:
            missing = ", ".join(sorted(missing_expected))
            raise ValueError(f"Parsed file is missing prompt columns: {missing}")

    def get_llm_columns(self, df_columns: list) -> list:
        llm_columns = [c for c in df_columns if c in self.llm_field_classes]
        return llm_columns

    def get_calc_columns(self) -> list:
        calc_columns = list(self.calc_field_classes)
        return calc_columns

    def get_output_columns(self) -> list[str]:
        columns = ["source", "text"]
        for field_class in self.llm_field_classes.values():
            columns += [
                c for c in field_class().get_visible_fields() if c not in columns
            ]
        for field_class in self.calc_field_classes.values():
            columns += [
                c for c in field_class().get_visible_fields() if c not in columns
            ]
        return columns
