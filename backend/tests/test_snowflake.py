from app.domain.snowflake import MAX_JS_SAFE_INTEGER, SnowflakeGenerator, created_at_ms


def test_snowflake_is_monotonic_and_js_safe() -> None:
    generator = SnowflakeGenerator(worker_id=1)

    first = generator.generate()
    second = generator.generate()

    assert first < second
    assert second <= MAX_JS_SAFE_INTEGER
    assert created_at_ms(first) <= created_at_ms(second)


def test_worker_id_range_is_enforced() -> None:
    try:
        SnowflakeGenerator(worker_id=64)
    except ValueError:
        return

    raise AssertionError("expected worker_id validation error")

