"""Tests for GenieACS binary sensor logic."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from custom_components.genieacs.const import ONLINE_THRESHOLD_SECONDS


def _is_device_online(last_inform) -> bool | None:
    """Replicate the online detection logic from the binary sensor."""
    if last_inform is None:
        return False
    try:
        if isinstance(last_inform, str):
            informed_at = datetime.fromisoformat(last_inform.replace("Z", "+00:00"))
        else:
            informed_at = datetime.fromtimestamp(last_inform / 1000, tz=UTC)
    except (ValueError, TypeError, OSError):
        return False
    threshold = datetime.now(UTC) - timedelta(seconds=ONLINE_THRESHOLD_SECONDS)
    return informed_at >= threshold


def test_online_threshold_is_300_seconds() -> None:
    """Verify the online threshold constant."""
    assert ONLINE_THRESHOLD_SECONDS == 300


def test_online_recent_iso_string() -> None:
    """Test device is online with recent ISO timestamp."""
    recent = datetime.now(UTC).isoformat()
    assert _is_device_online(recent) is True


def test_offline_old_iso_string() -> None:
    """Test device is offline with old ISO timestamp."""
    old = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    assert _is_device_online(old) is False


def test_offline_no_inform() -> None:
    """Test device is offline with no last inform."""
    assert _is_device_online(None) is False


def test_online_epoch_ms() -> None:
    """Test device is online with epoch millisecond timestamp."""
    now_ms = int(datetime.now(UTC).timestamp() * 1000)
    assert _is_device_online(now_ms) is True


def test_offline_old_epoch_ms() -> None:
    """Test device is offline with old epoch ms timestamp."""
    old_ms = int((datetime.now(UTC) - timedelta(hours=1)).timestamp() * 1000)
    assert _is_device_online(old_ms) is False


def test_online_z_suffix() -> None:
    """Test ISO timestamp with Z suffix."""
    recent = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    assert _is_device_online(recent) is True


def test_invalid_string() -> None:
    """Test invalid string returns False."""
    assert _is_device_online("not-a-date") is False
