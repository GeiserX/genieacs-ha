"""Tests for GenieACS button platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.genieacs.button import (
    BUTTON_DESCRIPTIONS,
    GenieAcsButton,
    GenieAcsButtonDescription,
    async_setup_entry,
)

from .conftest import MOCK_DEVICE_NORMALIZED, make_coordinator


# ---------------------------------------------------------------------------
# BUTTON_DESCRIPTIONS constants
# ---------------------------------------------------------------------------

def test_button_descriptions_count() -> None:
    """Test there are exactly two button descriptions (reboot + refresh)."""
    assert len(BUTTON_DESCRIPTIONS) == 2


def test_reboot_button_description() -> None:
    """Test reboot button description fields."""
    reboot = BUTTON_DESCRIPTIONS[0]
    assert reboot.key == "reboot"
    assert reboot.translation_key == "reboot"
    assert reboot.icon == "mdi:restart"


def test_refresh_button_description() -> None:
    """Test refresh button description fields."""
    refresh = BUTTON_DESCRIPTIONS[1]
    assert refresh.key == "refresh"
    assert refresh.translation_key == "refresh"
    assert refresh.icon == "mdi:refresh"


# ---------------------------------------------------------------------------
# GenieAcsButton
# ---------------------------------------------------------------------------

def test_button_unique_id() -> None:
    """Test that unique_id is composed of device_id and key."""
    coordinator = make_coordinator()
    button = GenieAcsButton(coordinator, "my-device", BUTTON_DESCRIPTIONS[0])
    assert button._attr_unique_id == "my-device_reboot"


def test_button_unique_id_refresh() -> None:
    """Test unique_id for the refresh button."""
    coordinator = make_coordinator()
    button = GenieAcsButton(coordinator, "my-device", BUTTON_DESCRIPTIONS[1])
    assert button._attr_unique_id == "my-device_refresh"


def test_button_entity_description_set() -> None:
    """Test that entity_description is set on the button."""
    coordinator = make_coordinator()
    desc = BUTTON_DESCRIPTIONS[0]
    button = GenieAcsButton(coordinator, "dev", desc)
    assert button.entity_description is desc


# ---------------------------------------------------------------------------
# async_press
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_reboot_press_calls_api() -> None:
    """Test pressing reboot calls async_reboot_device."""
    client = MagicMock()
    client.async_reboot_device = AsyncMock()
    client.async_get_devices = AsyncMock(return_value=[])
    client._nbi_url = "http://x:7557"

    coordinator = make_coordinator(client=client)
    coordinator.async_request_refresh = AsyncMock()

    button = GenieAcsButton(coordinator, "dev-123", BUTTON_DESCRIPTIONS[0])
    await button.async_press()

    client.async_reboot_device.assert_awaited_once_with("dev-123")
    coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_press_calls_api() -> None:
    """Test pressing refresh calls async_refresh_device."""
    client = MagicMock()
    client.async_refresh_device = AsyncMock()
    client.async_get_devices = AsyncMock(return_value=[])
    client._nbi_url = "http://x:7557"

    coordinator = make_coordinator(client=client)
    coordinator.async_request_refresh = AsyncMock()

    button = GenieAcsButton(coordinator, "dev-123", BUTTON_DESCRIPTIONS[1])
    await button.async_press()

    client.async_refresh_device.assert_awaited_once_with("dev-123")
    coordinator.async_request_refresh.assert_awaited_once()


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_setup_entry_creates_buttons() -> None:
    """Test that async_setup_entry creates 2 buttons per device."""
    coordinator = make_coordinator(devices={
        "dev1": MOCK_DEVICE_NORMALIZED,
        "dev2": {**MOCK_DEVICE_NORMALIZED, "device_id": "dev2"},
    })

    entry = MagicMock()
    entry.runtime_data = coordinator

    added: list = []
    hass = MagicMock()
    await async_setup_entry(hass, entry, added.extend)

    assert len(added) == 4  # 2 devices * 2 button types
    assert all(isinstance(e, GenieAcsButton) for e in added)


@pytest.mark.asyncio
async def test_async_setup_entry_no_devices() -> None:
    """Test no buttons created when there are no devices."""
    coordinator = make_coordinator(devices={})

    entry = MagicMock()
    entry.runtime_data = coordinator

    added: list = []
    hass = MagicMock()
    await async_setup_entry(hass, entry, added.extend)

    assert len(added) == 0


@pytest.mark.asyncio
async def test_async_setup_entry_single_device() -> None:
    """Test that a single device gets exactly 2 buttons."""
    coordinator = make_coordinator()

    entry = MagicMock()
    entry.runtime_data = coordinator

    added: list = []
    hass = MagicMock()
    await async_setup_entry(hass, entry, added.extend)

    assert len(added) == 2
    keys = {b._attr_unique_id.split("_", 1)[1] for b in added}
    assert keys == {"reboot", "refresh"}
