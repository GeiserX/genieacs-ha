"""Tests for GenieACS binary sensor platform."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.genieacs.binary_sensor import (
    GenieAcsOnlineBinarySensor,
    async_setup_entry,
)
from custom_components.genieacs.const import ONLINE_THRESHOLD_SECONDS

from .conftest import MOCK_DEVICE_NORMALIZED, make_coordinator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_online_threshold_is_300_seconds() -> None:
    """Verify the online threshold constant."""
    assert ONLINE_THRESHOLD_SECONDS == 300


# ---------------------------------------------------------------------------
# GenieAcsOnlineBinarySensor
# ---------------------------------------------------------------------------

def test_sensor_unique_id() -> None:
    """Test that unique_id is derived from device_id."""
    coordinator = make_coordinator()
    sensor = GenieAcsOnlineBinarySensor(coordinator, "001122-TestRouter-AABBCC")
    assert sensor._attr_unique_id == "001122-TestRouter-AABBCC_online"


def test_sensor_device_class() -> None:
    """Test the device class is connectivity."""
    coordinator = make_coordinator()
    sensor = GenieAcsOnlineBinarySensor(coordinator, "001122-TestRouter-AABBCC")
    assert sensor._attr_device_class.value if hasattr(sensor._attr_device_class, "value") else sensor._attr_device_class == "connectivity"


def test_sensor_translation_key() -> None:
    """Test the translation key."""
    coordinator = make_coordinator()
    sensor = GenieAcsOnlineBinarySensor(coordinator, "001122-TestRouter-AABBCC")
    assert sensor._attr_translation_key == "online"


# ---------------------------------------------------------------------------
# is_on property
# ---------------------------------------------------------------------------

def test_is_on_recent_iso_string() -> None:
    """Test device is online with recent ISO timestamp."""
    recent = datetime.now(UTC).isoformat()
    data = {**MOCK_DEVICE_NORMALIZED, "last_inform": recent}
    coordinator = make_coordinator(devices={"dev1": data})
    sensor = GenieAcsOnlineBinarySensor(coordinator, "dev1")
    assert sensor.is_on is True


def test_is_on_old_iso_string() -> None:
    """Test device is offline with old ISO timestamp."""
    old = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    data = {**MOCK_DEVICE_NORMALIZED, "last_inform": old}
    coordinator = make_coordinator(devices={"dev1": data})
    sensor = GenieAcsOnlineBinarySensor(coordinator, "dev1")
    assert sensor.is_on is False


def test_is_on_z_suffix() -> None:
    """Test ISO timestamp with Z suffix."""
    recent = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    data = {**MOCK_DEVICE_NORMALIZED, "last_inform": recent}
    coordinator = make_coordinator(devices={"dev1": data})
    sensor = GenieAcsOnlineBinarySensor(coordinator, "dev1")
    assert sensor.is_on is True


def test_is_on_epoch_ms() -> None:
    """Test device is online with epoch millisecond timestamp."""
    now_ms = int(datetime.now(UTC).timestamp() * 1000)
    data = {**MOCK_DEVICE_NORMALIZED, "last_inform": now_ms}
    coordinator = make_coordinator(devices={"dev1": data})
    sensor = GenieAcsOnlineBinarySensor(coordinator, "dev1")
    assert sensor.is_on is True


def test_is_on_old_epoch_ms() -> None:
    """Test device is offline with old epoch ms timestamp."""
    old_ms = int((datetime.now(UTC) - timedelta(hours=1)).timestamp() * 1000)
    data = {**MOCK_DEVICE_NORMALIZED, "last_inform": old_ms}
    coordinator = make_coordinator(devices={"dev1": data})
    sensor = GenieAcsOnlineBinarySensor(coordinator, "dev1")
    assert sensor.is_on is False


def test_is_on_none_last_inform() -> None:
    """Test device is offline with no last inform."""
    data = {**MOCK_DEVICE_NORMALIZED, "last_inform": None}
    coordinator = make_coordinator(devices={"dev1": data})
    sensor = GenieAcsOnlineBinarySensor(coordinator, "dev1")
    assert sensor.is_on is False


def test_is_on_invalid_string() -> None:
    """Test invalid string returns False."""
    data = {**MOCK_DEVICE_NORMALIZED, "last_inform": "not-a-date"}
    coordinator = make_coordinator(devices={"dev1": data})
    sensor = GenieAcsOnlineBinarySensor(coordinator, "dev1")
    assert sensor.is_on is False


def test_is_on_missing_device_returns_none() -> None:
    """Test is_on returns None when device is not in coordinator data."""
    coordinator = make_coordinator(devices={})
    sensor = GenieAcsOnlineBinarySensor(coordinator, "missing-device")
    assert sensor.is_on is None


def test_is_on_no_last_inform_key() -> None:
    """Test device with no last_inform key at all."""
    data = {"device_id": "dev1", "manufacturer": "X", "model": "Y"}
    coordinator = make_coordinator(devices={"dev1": data})
    sensor = GenieAcsOnlineBinarySensor(coordinator, "dev1")
    assert sensor.is_on is False


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_setup_entry_creates_entities() -> None:
    """Test that async_setup_entry creates one entity per device."""
    coordinator = make_coordinator(devices={
        "dev1": MOCK_DEVICE_NORMALIZED,
        "dev2": {**MOCK_DEVICE_NORMALIZED, "device_id": "dev2"},
    })

    entry = MagicMock()
    entry.runtime_data = coordinator

    added_entities: list = []

    def capture(entities: list) -> None:
        added_entities.extend(entities)

    hass = MagicMock()
    await async_setup_entry(hass, entry, capture)

    assert len(added_entities) == 2
    assert all(isinstance(e, GenieAcsOnlineBinarySensor) for e in added_entities)


@pytest.mark.asyncio
async def test_async_setup_entry_no_devices() -> None:
    """Test that async_setup_entry creates no entities when there are no devices."""
    coordinator = make_coordinator(devices={})

    entry = MagicMock()
    entry.runtime_data = coordinator

    added_entities: list = []
    hass = MagicMock()
    await async_setup_entry(hass, entry, added_entities.extend)

    assert len(added_entities) == 0
