"""Tests for the GenieACS coordinator."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.genieacs.api import (
    GenieAcsApiClient,
    GenieAcsConnectionError,
    GenieAcsError,
)
from custom_components.genieacs.const import DEFAULT_SCAN_INTERVAL, DOMAIN
from custom_components.genieacs.coordinator import GenieAcsCoordinator

from .conftest import MOCK_DEVICE_NORMALIZED, make_coordinator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_default_scan_interval() -> None:
    """Verify default scan interval is 60 seconds."""
    assert DEFAULT_SCAN_INTERVAL == 60


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------

def test_coordinator_name() -> None:
    """Test coordinator name matches domain."""
    coordinator = make_coordinator()
    assert coordinator.name == DOMAIN


def test_coordinator_update_interval() -> None:
    """Test coordinator update interval."""
    coordinator = make_coordinator()
    assert coordinator.update_interval == timedelta(seconds=DEFAULT_SCAN_INTERVAL)


def test_coordinator_client_stored() -> None:
    """Test coordinator stores the client reference."""
    client = MagicMock()
    client._nbi_url = "http://x:7557"
    client.async_get_devices = AsyncMock(return_value=[])
    coordinator = make_coordinator(client=client)
    assert coordinator.client is client


# ---------------------------------------------------------------------------
# _async_update_data
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_data_returns_dict_keyed_by_device_id() -> None:
    """Test that _async_update_data returns data keyed by device_id."""
    client = MagicMock()
    client.async_get_devices = AsyncMock(return_value=[MOCK_DEVICE_NORMALIZED])
    client._nbi_url = "http://x:7557"

    coordinator = make_coordinator(client=client)
    data = await coordinator._async_update_data()

    assert "001122-TestRouter-AABBCC" in data
    assert data["001122-TestRouter-AABBCC"]["manufacturer"] == "TestMfg"


@pytest.mark.asyncio
async def test_update_data_multiple_devices() -> None:
    """Test handling multiple devices keyed properly."""
    device2 = {**MOCK_DEVICE_NORMALIZED, "device_id": "device-2", "manufacturer": "Other"}
    client = MagicMock()
    client.async_get_devices = AsyncMock(return_value=[MOCK_DEVICE_NORMALIZED, device2])
    client._nbi_url = "http://x:7557"

    coordinator = make_coordinator(client=client)
    data = await coordinator._async_update_data()

    assert len(data) == 2
    assert data["device-2"]["manufacturer"] == "Other"


@pytest.mark.asyncio
async def test_update_data_empty() -> None:
    """Test empty device list returns empty dict."""
    client = MagicMock()
    client.async_get_devices = AsyncMock(return_value=[])
    client._nbi_url = "http://x:7557"

    coordinator = make_coordinator(client=client)
    data = await coordinator._async_update_data()

    assert data == {}


@pytest.mark.asyncio
async def test_update_data_connection_error_raises_update_failed() -> None:
    """Test connection error is wrapped as UpdateFailed."""
    from homeassistant.helpers.update_coordinator import UpdateFailed

    client = MagicMock()
    client.async_get_devices = AsyncMock(
        side_effect=GenieAcsConnectionError("timeout")
    )
    client._nbi_url = "http://x:7557"

    coordinator = make_coordinator(client=client)
    with pytest.raises(UpdateFailed, match="Cannot reach"):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_update_data_generic_error_raises_update_failed() -> None:
    """Test generic GenieAcsError is wrapped as UpdateFailed."""
    from homeassistant.helpers.update_coordinator import UpdateFailed

    client = MagicMock()
    client.async_get_devices = AsyncMock(
        side_effect=GenieAcsError("bad data")
    )
    client._nbi_url = "http://x:7557"

    coordinator = make_coordinator(client=client)
    with pytest.raises(UpdateFailed, match="Error fetching"):
        await coordinator._async_update_data()


# ---------------------------------------------------------------------------
# Integration with async_config_entry_first_refresh
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_first_refresh_populates_data() -> None:
    """Test that async_config_entry_first_refresh calls _async_update_data."""
    client = MagicMock()
    client.async_get_devices = AsyncMock(return_value=[MOCK_DEVICE_NORMALIZED])
    client._nbi_url = "http://x:7557"

    hass = MagicMock()
    coordinator = GenieAcsCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    assert "001122-TestRouter-AABBCC" in coordinator.data
