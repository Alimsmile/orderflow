from zipfile import BadZipFile

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException


def parse_excel(file):
    try:
        workbook = load_workbook(
            file,
            read_only=True,
            data_only=True,
        )
    except (InvalidFileException, BadZipFile, OSError) as exc:
        raise ValueError("Не удалось прочитать Excel-файл") from exc

    try:
        sheet = workbook.active

        raw_headers = next(
            sheet.iter_rows(min_row=1, max_row=1, values_only=True),
            None,
        )

        if not raw_headers:
            raise ValueError("Excel-файл не содержит заголовков")

        headers = [
            str(value).strip().lower() if value is not None else ""
            for value in raw_headers
        ]

        rows = []

        for row_number, values in enumerate(
            sheet.iter_rows(min_row=2, values_only=True),
            start=2,
        ):
            # Пропускаем полностью пустые строки.
            if all(
                value is None or (
                    isinstance(value, str) and not value.strip()
                )
                for value in values
            ):
                continue

            rows.append((
                row_number,
                dict(zip(headers, values)),
            ))

        return headers, rows

    finally:
        workbook.close()