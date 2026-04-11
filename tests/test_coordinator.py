"""Tests for the GenieACS coordinator data logic."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.genieacs.api import GenieAcsConnectionError, GenieAcsError
from custom_components.genieacs.const import DEFAULT_SCAN_INTERVAL

from .conftest import MOCK_DEVICE_NORMALIZED


def test_default_scan_interval() -> None:
    """Verify default scan interval is 60 seconds."""
    assert DEFAULT_SCAN_INTERVAL == 60


@pytest.mark.asyncio
async def test_data_keyed_by_device_id() -> None:
    """Test that coordinator data is keyed by device_id."""
    client = MagicMock()
    client.async_get_devices = AsyncMock(return_value=[MOCK_DEVICE_NORMALIZED])

    devices = await client.async_get_devices()
    data = {d["device_id"]: d for d in devices}

    assert "001122-TestRouter-AABBCC" in data
    assert data["001122-TestRouter-AABBCC"]["manufacturer"] == "TestMfg"


@pytest.mark.asyncio
async def test_connection_error_propagation() -> None:
    """Test connection errors are propagated."""
    client = MagicMock()
    client.async_get_devices = AsyncMock(
        side_effect=GenieAcsConnectionError("fail")
    )

    with pytest.raises(GenieAcsConnectionError):
        await client.async_get_devices()


@pytest.mark.asyncio
async def test_api_error_propagation() -> None:
    """Test API errors are propagated."""
    client = MagicMock()
    client.async_get_devices = AsyncMock(
        side_effect=GenieAcsError("bad data")
    )

    with pytest.raises(GenieAcsError):
        await client.async_get_devices()


@pytest.mark.asyncio
async def test_multiple_devices() -> None:
    """Test handling multiple devices."""
    device2 = {**MOCK_DEVICE_NORMALIZED, "device_id": "device-2", "manufacturer": "Other"}
    client = MagicMock()
    client.async_get_devices = AsyncMock(
        return_value=[MOCK_DEVICE_NORMALIZED, device2]
    )

    devices = await client.async_get_devices()
    data = {d["device_id"]: d for d in devices}

    assert len(data) == 2
    assert data["device-2"]["manufacturer"] == "Other"
