"""Tests for GenieACS sensor platform."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.genieacs.sensor import (
    SENSOR_DESCRIPTIONS,
    GenieAcsSensor,
    GenieAcsSensorDescription,
    _safe_int,
    async_setup_entry,
)

from .conftest import MOCK_DEVICE_NORMALIZED, make_coordinator


# ---------------------------------------------------------------------------
# _safe_int
# ---------------------------------------------------------------------------

def test_safe_int_valid_int() -> None:
    assert _safe_int(42) == 42


def test_safe_int_valid_string() -> None:
    assert _safe_int("100") == 100


def test_safe_int_none() -> None:
    assert _safe_int(None) is None


def test_safe_int_invalid_string() -> None:
    assert _safe_int("abc") is None


def test_safe_int_float() -> None:
    assert _safe_int(42.7) == 42


def test_safe_int_empty_string() -> None:
    assert _safe_int("") is None


def test_safe_int_list() -> None:
    assert _safe_int([1, 2]) is None


def test_safe_int_zero() -> None:
    assert _safe_int(0) == 0


def test_safe_int_negative() -> None:
    assert _safe_int(-5) == -5


def test_safe_int_string_negative() -> None:
    assert _safe_int("-10") == -10


# ---------------------------------------------------------------------------
# SENSOR_DESCRIPTIONS
# ---------------------------------------------------------------------------

def test_sensor_descriptions_count() -> None:
    """Test there are 6 sensor descriptions."""
    assert len(SENSOR_DESCRIPTIONS) == 6


def test_sensor_description_keys() -> None:
    """Test the keys of all sensor descriptions."""
    keys = [d.key for d in SENSOR_DESCRIPTIONS]
    assert keys == ["wan_ip", "uptime", "firmware", "manufacturer", "model", "serial"]


def test_sensor_description_wan_ip_icon() -> None:
    assert SENSOR_DESCRIPTIONS[0].icon == "mdi:ip-network"


def test_sensor_description_uptime_unit() -> None:
    assert SENSOR_DESCRIPTIONS[1].native_unit_of_measurement == "s"


def test_sensor_description_firmware_category() -> None:
    assert SENSOR_DESCRIPTIONS[2].entity_category == "diagnostic"


# ---------------------------------------------------------------------------
# value_fn
# ---------------------------------------------------------------------------

def test_value_fn_wan_ip() -> None:
    assert SENSOR_DESCRIPTIONS[0].value_fn(MOCK_DEVICE_NORMALIZED) == "1.2.3.4"


def test_value_fn_uptime() -> None:
    assert SENSOR_DESCRIPTIONS[1].value_fn(MOCK_DEVICE_NORMALIZED) == 86400


def test_value_fn_firmware() -> None:
    assert SENSOR_DESCRIPTIONS[2].value_fn(MOCK_DEVICE_NORMALIZED) == "1.2.3"


def test_value_fn_manufacturer() -> None:
    assert SENSOR_DESCRIPTIONS[3].value_fn(MOCK_DEVICE_NORMALIZED) == "TestMfg"


def test_value_fn_model() -> None:
    assert SENSOR_DESCRIPTIONS[4].value_fn(MOCK_DEVICE_NORMALIZED) == "TestModel"


def test_value_fn_serial() -> None:
    assert SENSOR_DESCRIPTIONS[5].value_fn(MOCK_DEVICE_NORMALIZED) == "AABBCC"


def test_value_fn_missing_key() -> None:
    """Test value_fn returns None for missing keys."""
    data = {"device_id": "x"}
    assert SENSOR_DESCRIPTIONS[0].value_fn(data) is None


def test_value_fn_uptime_none() -> None:
    """Test uptime value_fn returns None for missing uptime."""
    data = {"uptime": None}
    assert SENSOR_DESCRIPTIONS[1].value_fn(data) is None


def test_value_fn_uptime_string() -> None:
    """Test uptime value_fn converts string to int."""
    data = {"uptime": "12345"}
    assert SENSOR_DESCRIPTIONS[1].value_fn(data) == 12345


# ---------------------------------------------------------------------------
# GenieAcsSensor
# ---------------------------------------------------------------------------

def test_sensor_unique_id() -> None:
    """Test sensor unique_id."""
    coordinator = make_coordinator()
    sensor = GenieAcsSensor(coordinator, "dev1", SENSOR_DESCRIPTIONS[0])
    assert sensor._attr_unique_id == "dev1_wan_ip"


def test_sensor_entity_description() -> None:
    """Test entity_description is set."""
    coordinator = make_coordinator()
    desc = SENSOR_DESCRIPTIONS[2]
    sensor = GenieAcsSensor(coordinator, "dev1", desc)
    assert sensor.entity_description is desc


def test_sensor_native_value() -> None:
    """Test native_value returns the correct value."""
    coordinator = make_coordinator(devices={
        "dev1": MOCK_DEVICE_NORMALIZED,
    })
    sensor = GenieAcsSensor(coordinator, "dev1", SENSOR_DESCRIPTIONS[0])
    assert sensor.native_value == "1.2.3.4"


def test_sensor_native_value_uptime() -> None:
    """Test native_value for uptime sensor."""
    coordinator = make_coordinator(devices={
        "dev1": MOCK_DEVICE_NORMALIZED,
    })
    sensor = GenieAcsSensor(coordinator, "dev1", SENSOR_DESCRIPTIONS[1])
    assert sensor.native_value == 86400


def test_sensor_native_value_missing_device() -> None:
    """Test native_value returns None when device is missing."""
    coordinator = make_coordinator(devices={})
    sensor = GenieAcsSensor(coordinator, "missing", SENSOR_DESCRIPTIONS[0])
    assert sensor.native_value is None


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_setup_entry_creates_sensors() -> None:
    """Test that async_setup_entry creates 6 sensors per device."""
    coordinator = make_coordinator(devices={
        "dev1": MOCK_DEVICE_NORMALIZED,
    })

    entry = MagicMock()
    entry.runtime_data = coordinator

    added: list = []
    hass = MagicMock()
    await async_setup_entry(hass, entry, added.extend)

    assert len(added) == 6
    assert all(isinstance(e, GenieAcsSensor) for e in added)


@pytest.mark.asyncio
async def test_async_setup_entry_multiple_devices() -> None:
    """Test entities scale with device count."""
    coordinator = make_coordinator(devices={
        "dev1": MOCK_DEVICE_NORMALIZED,
        "dev2": {**MOCK_DEVICE_NORMALIZED, "device_id": "dev2"},
        "dev3": {**MOCK_DEVICE_NORMALIZED, "device_id": "dev3"},
    })

    entry = MagicMock()
    entry.runtime_data = coordinator

    added: list = []
    hass = MagicMock()
    await async_setup_entry(hass, entry, added.extend)

    assert len(added) == 18  # 3 devices * 6 sensor types


@pytest.mark.asyncio
async def test_async_setup_entry_no_devices() -> None:
    """Test no sensors when there are no devices."""
    coordinator = make_coordinator(devices={})

    entry = MagicMock()
    entry.runtime_data = coordinator

    added: list = []
    hass = MagicMock()
    await async_setup_entry(hass, entry, added.extend)

    assert len(added) == 0
