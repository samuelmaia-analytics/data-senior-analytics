import json
import logging
import time

from src.utils.observability import JsonFormatter, get_structured_logger, new_trace_id, timed_stage


def test_json_formatter_includes_standard_and_extra_fields():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="unit",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.trace_id = "abc123"

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "unit"
    assert payload["message"] == "hello"
    assert payload["trace_id"] == "abc123"


def test_get_structured_logger_reuses_existing_handler():
    logger_a = get_structured_logger("analytics-test")
    logger_b = get_structured_logger("analytics-test")

    assert logger_a is logger_b
    assert len(logger_a.handlers) == 1


def test_new_trace_id_returns_short_unique_values():
    trace_a = new_trace_id()
    trace_b = new_trace_id()

    assert len(trace_a) == 12
    assert len(trace_b) == 12
    assert trace_a != trace_b


def test_timed_stage_returns_timer_with_elapsed_ms():
    with timed_stage("load") as timer:
        time.sleep(0.01)

    assert timer.name == "load"
    assert timer.elapsed_ms > 0
