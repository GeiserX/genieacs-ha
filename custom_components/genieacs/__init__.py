"""GenieACS integration for Home Assistant."""

from __future__ import annotations

import logging

from aiohttp import ClientSession
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GenieAcsApiClient
from .const import CONF_NBI_URL, DOMAIN
from .coordinator import GenieAcsCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SENSOR,
]

type GenieAcsConfigEntry = ConfigEntry[GenieAcsCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: GenieAcsConfigEntry) -> bool:
    """Set up GenieACS from a config entry."""
    session: ClientSession = async_get_clientsession(hass)
    client = GenieAcsApiClient(
        session=session,
        nbi_url=entry.data[CONF_NBI_URL],
        username=entry.data.get(CONF_USERNAME),
        password=entry.data.get(CONF_PASSWORD),
    )

    coordinator = GenieAcsCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GenieAcsConfigEntry) -> bool:
    """Unload a GenieACS config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
