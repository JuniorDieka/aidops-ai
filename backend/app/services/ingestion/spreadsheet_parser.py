from pathlib import Path

import pandas as pd

from app.core.exceptions import IngestionError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class SpreadsheetParser:
    async def parse(self, file_path: str) -> list[dict[str, str | int]]:
        try:
            return await self._parse_spreadsheet(file_path)
        except Exception as e:
            logger.error("spreadsheet_parse_failed", error=str(e), file_path=file_path)
            raise IngestionError(f"Failed to parse spreadsheet: {str(e)}")

    async def _parse_spreadsheet(self, file_path: str) -> list[dict[str, str | int]]:
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._parse_spreadsheet_sync, file_path)

    def _parse_spreadsheet_sync(self, file_path: str) -> list[dict[str, str | int]]:
        file_extension = Path(file_path).suffix.lower()

        if file_extension == ".csv":
            df = pd.read_csv(file_path)
        elif file_extension in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path, sheet_name=None)
            if isinstance(df, dict):
                all_sheets = []
                for sheet_name, sheet_df in df.items():
                    sheet_text = self._dataframe_to_text(sheet_df, sheet_name)
                    all_sheets.append({"page": None, "section": sheet_name, "content": sheet_text})
                logger.info(
                    "spreadsheet_parsed", file_path=file_path, sheets=len(all_sheets)
                )
                return all_sheets
            else:
                df = df
        else:
            raise IngestionError(f"Unsupported spreadsheet format: {file_extension}")

        text = self._dataframe_to_text(df)
        logger.info("spreadsheet_parsed", file_path=file_path, rows=len(df))

        return [{"page": None, "content": text}]

    def _dataframe_to_text(self, df: pd.DataFrame, sheet_name: str | None = None) -> str:
        lines = []

        if sheet_name:
            lines.append(f"Sheet: {sheet_name}")
            lines.append("")

        lines.append("Columns: " + ", ".join(df.columns.astype(str)))
        lines.append("")

        for idx, row in df.iterrows():
            row_text = " | ".join(f"{col}: {val}" for col, val in row.items())
            lines.append(f"Row {idx + 1}: {row_text}")

        summary_stats = df.describe(include="all").to_string()
        lines.append("")
        lines.append("Summary Statistics:")
        lines.append(summary_stats)

        return "\n".join(lines)
