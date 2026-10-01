@pytest.mark.integration
def test_receive_all_10_signals():
    """
    Критический интеграционный тест.

    Предусловие:
        сервис-симулятор запущен и слушает TCP-порт 2001.

    Проверяем:
        1. Устанавливается TCP-соединение с сервисом.
        2. Получено ровно 10 сигналов.
        3. Каждый сигнал содержит обязательные поля.
        4. Типы полей соответствуют контракту.
        5. ID сигналов уникальны и находятся в диапазоне 1–10.
        6. Значения сигналов не являются одинаковыми.
    """

    signals = receive_signals(HOST, PORT, EXPECTED_SIGNALS)

    # 1. Проверяем количество полученных сигналов

    assert len(signals) == EXPECTED_SIGNALS, (
        f"Ожидалось {EXPECTED_SIGNALS} сигналов, "
        f"получено {len(signals)}"
    )
    # 2. Проверяем обязательные поля

    required_fields = {
        "id",
        "name",
        "value",
        "quality",
        "time",
    }

    for index, signal in enumerate(signals, start=1):
        missing_fields = required_fields - signal.keys()

        assert not missing_fields, (
            f"Сигнал #{index} не содержит обязательные поля: "
            f"{missing_fields}. "
            f"Получен сигнал: {signal}"
        )
    # 3. Проверяем типы данных

    type_checks = {
        "id": int,
        "name": str,
        "value": (int, float),
        "quality": bool,
        "time": int,
    }

    for index, signal in enumerate(signals, start=1):
        for field, expected_type in type_checks.items():
            actual_value = signal[field]
            if expected_type is bool:
                is_valid = type(actual_value) is bool
            else:
                is_valid = isinstance(actual_value, expected_type)

            # Формируем читаемое описание ожидаемого типа.
            if isinstance(expected_type, tuple):
                expected_type_name = " или ".join(
                    t.__name__ for t in expected_type
                )
            else:
                expected_type_name = expected_type.__name__

            assert is_valid, (
                f"Сигнал #{index}: поле '{field}' "
                f"имеет значение {actual_value!r} "
                f"типа {type(actual_value).__name__}, "
                f"ожидался {expected_type_name}"
            )
    # 4. Проверяем уникальность ID

    signal_ids = [signal["id"] for signal in signals]

    assert len(signal_ids) == len(set(signal_ids)), (
        f"Обнаружены дублирующиеся ID: {signal_ids}"
    )
    # 5. Проверяем ID сигналов

    expected_ids = list(range(1, EXPECTED_SIGNALS + 1))

    assert sorted(signal_ids) == expected_ids, (
        f"Ожидались ID {expected_ids}, "
        f"получены {sorted(signal_ids)}"
    )
    # 6. Проверяем, что значения сигналов различаются

    values = [signal["value"] for signal in signals]

    assert len(set(values)) > 1, (
        "Все значения сигналов одинаковые. "
        "Ожидались изменяющиеся значения "
        "(синусоида/случайные значения)"
    )
