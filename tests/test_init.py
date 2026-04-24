"""Tests for the GenieACS integration __init__ module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.genieacs import (
    PLATFORMS,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.genieacs.const import CONF_NBI_URL, DOMAIN

from .conftest import MOCK_DEVICE_NORMALIZED


# ---------------------------------------------------------------------------
# PLATFORMS constant
# ---------------------------------------------------------------------------

def test_platforms_list() -> None:
    """Test the PLATFORMS list contains expected platforms."""
    assert "binary_sensor" in PLATFORMS
    assert "button" in PLATFORMS
    assert "sensor" in PLATFORMS
    assert len(PLATFORMS) == 3


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_setup_entry_success() -> None:
    """Test successful setup of a config entry."""
    mock_session = MagicMock()

    mock_client = MagicMock()
    mock_client.async_get_devices = AsyncMock(return_value=[MOCK_DEVICE_NORMALIZED])
    mock_client._nbi_url = "http://genieacs:7557"

    hass = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()

    entry = MagicMock()
    entry.data = {
        CONF_NBI_URL: "http://genieacs:7557",
        "username": "admin",
        "password": "secret",
    }
    entry.runtime_data = None

    with patch(
        "custom_components.genieacs.async_get_clientsession",
        return_value=mock_session,
    ), patch(
        "custom_components.genieacs.GenieAcsApiClient",
        return_value=mock_client,
    ), patch(
        "custom_components.genieacs.GenieAcsCoordinator",
    ) as mock_coord_cls:
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coord_cls.return_value = mock_coordinator

        result = await async_setup_entry(hass, entry)

    assert result is True
    mock_coordinator.async_config_entry_first_refresh.assert_awaited_once()
    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
        entry, PLATFORMS
    )
    assert entry.runtime_data is mock_coordinator


@pytest.mark.asyncio
async def test_async_setup_entry_no_auth() -> None:
    """Test setup when no credentials are provided."""
    mock_session = MagicMock()

    mock_client = MagicMock()
    mock_client.async_get_devices = AsyncMock(return_value=[])
    mock_client._nbi_url = "http://genieacs:7557"

    hass = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()

    entry = MagicMock()
    entry.data = {
        CONF_NBI_URL: "http://genieacs:7557",
    }
    entry.runtime_data = None

    with patch(
        "custom_components.genieacs.async_get_clientsession",
        return_value=mock_session,
    ), patch(
        "custom_components.genieacs.GenieAcsApiClient",
        return_value=mock_client,
    ) as mock_client_cls, patch(
        "custom_components.genieacs.GenieAcsCoordinator",
    ) as mock_coord_cls:
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coord_cls.return_value = mock_coordinator

        result = await async_setup_entry(hass, entry)

    assert result is True
    # Verify client was created with None for username and password
    call_kwargs = mock_client_cls.call_args
    assert call_kwargs.kwargs.get("username") is None or call_kwargs[1].get("username") is None


# ---------------------------------------------------------------------------
# async_unload_entry
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_unload_entry() -> None:
    """Test unloading a config entry."""
    hass = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    entry = MagicMock()

    result = await async_unload_entry(hass, entry)

    assert result is True
    hass.config_entries.async_unload_platforms.assert_awaited_once_with(
        entry, PLATFORMS
    )


@pytest.mark.asyncio
async def test_async_unload_entry_failure() -> None:
    """Test unload returns False when platform unloading fails."""
    hass = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)

    entry = MagicMock()

    result = await async_unload_entry(hass, entry)

    assert result is False
