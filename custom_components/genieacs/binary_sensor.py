"""Binary sensor platform for GenieACS."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import GenieAcsConfigEntry
from .const import DOMAIN, ONLINE_THRESHOLD_SECONDS
from .coordinator import GenieAcsCoordinator
from .entity import GenieAcsEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GenieAcsConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GenieACS binary sensors from a config entry."""
    coordinator: GenieAcsCoordinator = entry.runtime_data
    entities: list[GenieAcsOnlineBinarySensor] = [
        GenieAcsOnlineBinarySensor(coordinator, device_id)
        for device_id in coordinator.data
    ]
    async_add_entities(entities)


class GenieAcsOnlineBinarySensor(GenieAcsEntity, BinarySensorEntity):
    """Binary sensor indicating whether a CPE device is online."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_translation_key = "online"

    def __init__(
        self,
        coordinator: GenieAcsCoordinator,
        device_id: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_online"

    @property
    def is_on(self) -> bool | None:
        """Return True if the device reported within the last 5 minutes."""
        data = self.device_data
        if data is None:
            return None
        last_inform = data.get("last_inform")
        if last_inform is None:
            return False
        try:
            if isinstance(last_inform, str):
                informed_at = datetime.fromisoformat(last_inform.replace("Z", "+00:00"))
            else:
                informed_at = datetime.fromtimestamp(last_inform / 1000, tz=UTC)
        except (ValueError, TypeError, OSError):
            return False
        threshold = datetime.now(UTC) - timedelta(seconds=ONLINE_THRESHOLD_SECONDS)
        return informed_at >= threshold
