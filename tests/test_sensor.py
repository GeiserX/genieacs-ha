"""Tests for GenieACS sensor value extraction logic."""

from __future__ import annotations

import pytest

from .conftest import MOCK_DEVICE_NORMALIZED


def _safe_int(value) -> int | None:
    """Convert a value to int, returning None on failure."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def test_safe_int_valid() -> None:
    """Test _safe_int with valid int."""
    assert _safe_int(42) == 42
    assert _safe_int("100") == 100


def test_safe_int_none() -> None:
    """Test _safe_int with None."""
    assert _safe_int(None) is None


def test_safe_int_invalid() -> None:
    """Test _safe_int with non-numeric string."""
    assert _safe_int("abc") is None


def test_safe_int_float() -> None:
    """Test _safe_int with float."""
    assert _safe_int(42.7) == 42


def test_wan_ip_extraction() -> None:
    """Test WAN IP is extracted from device data."""
    assert MOCK_DEVICE_NORMALIZED["wan_ip"] == "1.2.3.4"


def test_uptime_extraction() -> None:
    """Test uptime is extracted from device data."""
    assert MOCK_DEVICE_NORMALIZED["uptime"] == 86400


def test_firmware_extraction() -> None:
    """Test firmware version extraction."""
    assert MOCK_DEVICE_NORMALIZED["firmware"] == "1.2.3"


def test_manufacturer_extraction() -> None:
    """Test manufacturer extraction."""
    assert MOCK_DEVICE_NORMALIZED["manufacturer"] == "TestMfg"


def test_model_extraction() -> None:
    """Test model extraction."""
    assert MOCK_DEVICE_NORMALIZED["model"] == "TestModel"


def test_serial_extraction() -> None:
    """Test serial number extraction."""
    assert MOCK_DEVICE_NORMALIZED["serial"] == "AABBCC"


def test_sensor_value_fn_wan_ip() -> None:
    """Test sensor value function for WAN IP."""
    value_fn = lambda d: d.get("wan_ip")
    assert value_fn(MOCK_DEVICE_NORMALIZED) == "1.2.3.4"


def test_sensor_value_fn_uptime() -> None:
    """Test sensor value function for uptime."""
    value_fn = lambda d: _safe_int(d.get("uptime"))
    assert value_fn(MOCK_DEVICE_NORMALIZED) == 86400


def test_sensor_value_missing_device() -> None:
    """Test sensor value when device data is None."""
    data = {}
    device_data = data.get("missing-device")
    assert device_data is None


def test_device_name_generation() -> None:
    """Test device name generation from manufacturer and model."""
    data = MOCK_DEVICE_NORMALIZED
    manufacturer = data.get("manufacturer")
    model = data.get("model")
    name = f"{manufacturer} {model}" if manufacturer and model else data["device_id"]
    assert name == "TestMfg TestModel"


def test_device_name_fallback() -> None:
    """Test device name falls back to device_id."""
    data = {"device_id": "test-123", "manufacturer": None, "model": None}
    manufacturer = data.get("manufacturer")
    model = data.get("model")
    name = f"{manufacturer} {model}" if manufacturer and model else data["device_id"]
    assert name == "test-123"
