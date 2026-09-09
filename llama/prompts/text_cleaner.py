from typing import TYPE_CHECKING

from llama.prompts.prompt_markdown_parser import PromptMarkdownParser

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd

    from llama.prompts.prompt import Prompt

REQUIRED_PARSED_COLUMNS = {"status", "source", "text"}


class TextCleaner:
    def __init__(self, prompt_md: Path) -> None:
        prompt_parser = PromptMarkdownParser(prompt_md)
        self.llm_field_classes = {
            f.name: f.field_class for f in prompt_parser.llm_fields
        }
        self.calc_field_classes = {
            f.name: f.field_class for f in prompt_parser.calc_fields
        }

    def validate_columns(
        self, df_columns: list[str] | pd.Index, prompt: Prompt
    ) -> None:
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
