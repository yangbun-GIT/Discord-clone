from __future__ import annotations

import threading
import time
from datetime import UTC, datetime

MAX_JS_SAFE_INTEGER = 2**53 - 1
CUSTOM_EPOCH_MS = int(datetime(2026, 1, 1, tzinfo=UTC).timestamp() * 1000)

TIMESTAMP_BITS = 39
WORKER_BITS = 6
SEQUENCE_BITS = 8

MAX_WORKER_ID = (1 << WORKER_BITS) - 1
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1

WORKER_SHIFT = SEQUENCE_BITS
TIMESTAMP_SHIFT = WORKER_BITS + SEQUENCE_BITS


class SnowflakeGenerator:
    def __init__(self, worker_id: int = 0) -> None:
        if worker_id < 0 or worker_id > MAX_WORKER_ID:
            raise ValueError(f"worker_id must be between 0 and {MAX_WORKER_ID}")
        self._worker_id = worker_id
        self._last_timestamp = -1
        self._sequence = 0
        self._lock = threading.Lock()

    def generate(self) -> int:
        with self._lock:
            timestamp = current_timestamp_ms()
            if timestamp < self._last_timestamp:
                raise RuntimeError("clock moved backwards")

            if timestamp == self._last_timestamp:
                self._sequence = (self._sequence + 1) & MAX_SEQUENCE
                if self._sequence == 0:
                    timestamp = wait_next_millisecond(self._last_timestamp)
            else:
                self._sequence = 0

            self._last_timestamp = timestamp
            value = (
                ((timestamp - CUSTOM_EPOCH_MS) << TIMESTAMP_SHIFT)
                | (self._worker_id << WORKER_SHIFT)
                | self._sequence
            )
            if value > MAX_JS_SAFE_INTEGER:
                raise OverflowError("generated ID exceeds JavaScript safe integer range")
            return value


def current_timestamp_ms() -> int:
    return int(time.time() * 1000)


def wait_next_millisecond(previous_timestamp: int) -> int:
    timestamp = current_timestamp_ms()
    while timestamp <= previous_timestamp:
        timestamp = current_timestamp_ms()
    return timestamp


def created_at_ms(snowflake: int) -> int:
    return (snowflake >> TIMESTAMP_SHIFT) + CUSTOM_EPOCH_MS

