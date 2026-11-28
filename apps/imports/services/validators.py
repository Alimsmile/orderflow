from collections import Counter
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def validate_identifier(value):
    """Проверяет числовой идентификатор."""
    if isinstance(value, bool):
        return False

    if isinstance(value, int):
        return value > 0

    if isinstance(value, str):
        return value.strip().isdigit() and int(value.strip()) > 0

    return False


def validate_sku(value):
    """Проверяет артикул товара."""
    return isinstance(value, (str, int)) and bool(str(value).strip())


def validate_text(value):
    """Проверяет текстовое значение."""
    return isinstance(value, str) and bool(value.strip())


def validate_date(value):
    """Проверяет дату заказа."""
    if isinstance(value, (datetime, date)):
        return True

    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
            try:
                datetime.strptime(value.strip(), fmt)
                return True
            except ValueError:
                continue

    return False


def validate_quantity(value):
    """Количество должно быть целым числом больше нуля."""
    if isinstance(value, bool):
        return False

    if isinstance(value, int):
        return value > 0

    if isinstance(value, float):
        return value.is_integer() and value > 0

    if isinstance(value, str):
        return value.strip().isdigit() and int(value.strip()) > 0

    return False


def validate_price(value):
    """Цена должна быть числом не меньше нуля."""
    if isinstance(value, bool):
        return False

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return False

    return number.is_finite() and number >= 0


FIELD_VALIDATORS = {
    "order_id": ("идентификатором заказа", validate_identifier),
    "order_date": ("датой", validate_date),
    "customer_id": ("идентификатором покупателя", validate_identifier),
    "customer_name": ("текстовым значением", validate_text),
    "product_sku": ("артикулом товара", validate_sku),
    "product_name": ("текстовым значением", validate_text),
    "category_id": ("идентификатором категории", validate_identifier),
    "category_name": ("текстовым значением", validate_text),
    "quantity": ("положительным целым числом", validate_quantity),
    "price": ("числом не меньше нуля", validate_price),
}


def is_empty(value):
    return value is None or (
        isinstance(value, str) and not value.strip()
    )


def validate_columns(headers):
    headers = [str(header).strip() if header is not None else "" for header in headers]

    # Проверяем наличие всех обязательных колонок.
    required_columns = set(FIELD_VALIDATORS)
    missing_columns = required_columns - set(headers)

    if missing_columns:
        raise ValueError(
            f"Отсутствуют обязательные колонки: "
            f"{', '.join(sorted(missing_columns))}"
        )

    duplicates = [
        column
        for column, count in Counter(headers).items()
        if count > 1 and column
    ]

    if duplicates:
        raise ValueError(
            f"Обнаружены дублирующиеся колонки: "
            f"{', '.join(sorted(duplicates))}"
        )


def validate_rows(rows):
    if not rows:
        raise ValueError("Excel-файл не содержит данных")

    errors = []

    for row_number, row in rows:
        for field, (expected, validator) in FIELD_VALIDATORS.items():
            value = row.get(field)

            if is_empty(value):
                errors.append(
                    f"Строка {row_number}: пустое поле '{field}'"
                )
                continue

            if not validator(value):
                errors.append(
                    f"Строка {row_number}: поле '{field}' "
                    f"должно быть {expected}. Получено: {value!r}"
                )

    if errors:
        raise ValueError("\n".join(errors))

    # TODO: Уточнить бизнес-правила:
    # - Может ли один заказ содержать несколько покупателей?
    # - Может ли один товар повторяться в рамках одного заказа?