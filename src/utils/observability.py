"""Observability helpers for structured logging and execution timing."""

from __future__ import annotations

import json
import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass


class JsonFormatter(logging.Formatter):
    """Emit log records as JSON lines."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record, self.datefmt),
        }
        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key
            not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            }
        }
        payload.update(extras)
        return json.dumps(payload, default=str, ensure_ascii=False)


def get_structured_logger(name: str = "app") -> logging.Logger:
    """Create or reuse a JSON logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def new_trace_id() -> str:
    """Return a short unique trace id for request-scoped logs."""
    return uuid.uuid4().hex[:12]


@dataclass
class StageTimer:
    name: str
    start: float

    @property
    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self.start) * 1000.0


@contextmanager
def timed_stage(stage_name: str):
    """Context manager that measures elapsed time in milliseconds."""
    timer = StageTimer(name=stage_name, start=time.perf_counter())
    yield timer
