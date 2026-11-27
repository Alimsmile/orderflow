REQUIRED_COLUMNS = {
    "order_id",
    "order_date",
    "customer_id",
    "customer_name",
    "product_sku",
    "product_name",
    "category_id",
    "category_name",
    "quantity",
    "price",
}


def validate_columns(headers):
    # Проверяем наличие всех обязательных колонок.
    missing_columns = REQUIRED_COLUMNS - set(headers)

    if missing_columns:
        raise ValueError(
            f"Отсутствуют обязательные колонки: "
            f"{', '.join(sorted(missing_columns))}"
        )

    # TODO: Проверить наличие дублирующихся названий колонок.


def validate_rows(rows):
    if not rows:
        raise ValueError("Excel-файл не содержит данных")

    errors = []

    for row_number, row in rows:
        for field in REQUIRED_COLUMNS:
            value = row.get(field)

            if value is None or (
                isinstance(value, str) and not value.strip()
            ):
                errors.append(
                    f"Строка {row_number}: пустое поле '{field}'"
                )

    if errors:
        raise ValueError("\n".join(errors))

    # TODO: Проверить корректность типов данных.
    # TODO: Проверить формат даты.
    # TODO: quantity должен быть целым числом больше нуля.
    # TODO: price должен быть числом не меньше нуля.
    # TODO: Проверить дублирование заказов и товарных позиций.
    # TODO: Проверить корректность внешних идентификаторов.