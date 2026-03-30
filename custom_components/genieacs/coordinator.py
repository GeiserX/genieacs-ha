"""DataUpdateCoordinator for GenieACS."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GenieAcsApiClient, GenieAcsConnectionError, GenieAcsError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

type GenieAcsConfigEntry = ConfigEntry[GenieAcsCoordinator]


class GenieAcsCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Coordinator that polls GenieACS NBI for device data."""

    config_entry: GenieAcsConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: GenieAcsApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch devices from GenieACS and return a dict keyed by device_id."""
        try:
            devices = await self.client.async_get_devices()
        except GenieAcsConnectionError as err:
            raise UpdateFailed(f"Cannot reach GenieACS NBI: {err}") from err
        except GenieAcsError as err:
            raise UpdateFailed(f"Error fetching GenieACS devices: {err}") from err

        return {d["device_id"]: d for d in devices}
