"""Tests for the GenieACS base entity."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.genieacs.api import GenieAcsApiClient
from custom_components.genieacs.const import DOMAIN
from custom_components.genieacs.entity import GenieAcsEntity

from .conftest import (
    MOCK_DEVICE_NORMALIZED,
    MOCK_DEVICE_RAW_DEVICEID_ONLY,
    make_coordinator,
)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_entity_stores_device_id() -> None:
    """Test that entity stores the device_id."""
    coordinator = make_coordinator()
    entity = GenieAcsEntity(coordinator, "my-device")
    assert entity._device_id == "my-device"


def test_entity_has_entity_name() -> None:
    """Test _attr_has_entity_name is True."""
    coordinator = make_coordinator()
    entity = GenieAcsEntity(coordinator, "dev")
    assert entity._attr_has_entity_name is True


# ---------------------------------------------------------------------------
# device_data
# ---------------------------------------------------------------------------

def test_device_data_returns_data() -> None:
    """Test device_data returns data when device exists."""
    coordinator = make_coordinator()
    entity = GenieAcsEntity(coordinator, "001122-TestRouter-AABBCC")
    assert entity.device_data is not None
    assert entity.device_data["manufacturer"] == "TestMfg"


def test_device_data_returns_none_when_missing() -> None:
    """Test device_data returns None when device is missing."""
    coordinator = make_coordinator(devices={})
    entity = GenieAcsEntity(coordinator, "nonexistent")
    assert entity.device_data is None


# ---------------------------------------------------------------------------
# available
# ---------------------------------------------------------------------------

def test_available_when_data_present() -> None:
    """Test entity is available when device data exists."""
    coordinator = make_coordinator()
    coordinator.last_update_success = True
    entity = GenieAcsEntity(coordinator, "001122-TestRouter-AABBCC")
    assert entity.available is True


def test_not_available_when_data_missing() -> None:
    """Test entity is not available when device data is missing."""
    coordinator = make_coordinator(devices={})
    coordinator.last_update_success = True
    entity = GenieAcsEntity(coordinator, "nonexistent")
    assert entity.available is False


def test_not_available_when_coordinator_fails() -> None:
    """Test entity is not available when coordinator last update failed."""
    coordinator = make_coordinator()
    coordinator.last_update_success = False
    entity = GenieAcsEntity(coordinator, "001122-TestRouter-AABBCC")
    assert entity.available is False


# ---------------------------------------------------------------------------
# device_info
# ---------------------------------------------------------------------------

def test_device_info_with_full_data() -> None:
    """Test device_info with complete device data."""
    coordinator = make_coordinator()
    entity = GenieAcsEntity(coordinator, "001122-TestRouter-AABBCC")
    info = entity.device_info

    assert info.identifiers == {(DOMAIN, "001122-TestRouter-AABBCC")}
    assert info.name == "TestMfg TestModel"
    assert info.manufacturer == "TestMfg"
    assert info.model == "TestModel"
    assert info.sw_version == "1.2.3"
    assert info.configuration_url == "http://genieacs:7557"


def test_device_info_fallback_name() -> None:
    """Test device_info name falls back to device_id when no manufacturer/model."""
    data = {
        "device_id": "bare-device",
        "manufacturer": None,
        "model": None,
        "firmware": None,
    }
    coordinator = make_coordinator(devices={"bare-device": data})
    entity = GenieAcsEntity(coordinator, "bare-device")
    info = entity.device_info

    assert info.name == "bare-device"
    assert info.manufacturer is None
    assert info.model is None


def test_device_info_missing_manufacturer_only() -> None:
    """Test name fallback when only manufacturer is missing."""
    data = {
        "device_id": "dev-x",
        "manufacturer": None,
        "model": "SomeModel",
        "firmware": "2.0",
    }
    coordinator = make_coordinator(devices={"dev-x": data})
    entity = GenieAcsEntity(coordinator, "dev-x")
    info = entity.device_info

    assert info.name == "dev-x"


def test_device_info_missing_model_only() -> None:
    """Test name fallback when only model is missing."""
    data = {
        "device_id": "dev-y",
        "manufacturer": "Mfg",
        "model": None,
        "firmware": "3.0",
    }
    coordinator = make_coordinator(devices={"dev-y": data})
    entity = GenieAcsEntity(coordinator, "dev-y")
    info = entity.device_info

    assert info.name == "dev-y"


def test_device_info_when_no_device_data() -> None:
    """Test device_info uses empty dict when device data is None."""
    coordinator = make_coordinator(devices={})
    entity = GenieAcsEntity(coordinator, "gone-device")
    info = entity.device_info

    # Should not raise; uses device_id as name
    assert info.name == "gone-device"
    assert info.identifiers == {(DOMAIN, "gone-device")}


def test_device_info_name_from_device_id_fallback() -> None:
    """A device known only by _deviceId is named "<manufacturer> <product class>"."""
    client = GenieAcsApiClient.__new__(GenieAcsApiClient)
    data = client._normalize_device(MOCK_DEVICE_RAW_DEVICEID_ONLY)
    coordinator = make_coordinator(devices={data["device_id"]: data})
    entity = GenieAcsEntity(coordinator, data["device_id"])
    info = entity.device_info

    assert info.name == "SimMfg SimRouter"
    assert info.manufacturer == "SimMfg"
    assert info.model == "SimRouter"


def test_device_info_name_falls_back_to_serial() -> None:
    """Without manufacturer and model, the serial names the device, not the raw id."""
    data = {
        "device_id": "A1B2C3-SimRouter-SN0002",
        "manufacturer": None,
        "model": None,
        "serial": "SN0002",
        "firmware": None,
    }
    coordinator = make_coordinator(devices={data["device_id"]: data})
    entity = GenieAcsEntity(coordinator, data["device_id"])

    assert entity.device_info.name == "SN0002"
