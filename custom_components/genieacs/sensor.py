"""Sensor platform for GenieACS."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import GenieAcsConfigEntry
from .coordinator import GenieAcsCoordinator
from .entity import GenieAcsEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class GenieAcsSensorDescription(SensorEntityDescription):
    """Describe a GenieACS sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSOR_DESCRIPTIONS: tuple[GenieAcsSensorDescription, ...] = (
    GenieAcsSensorDescription(
        key="wan_ip",
        translation_key="wan_ip",
        icon="mdi:ip-network",
        value_fn=lambda d: d.get("wan_ip"),
    ),
    GenieAcsSensorDescription(
        key="uptime",
        translation_key="uptime",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        icon="mdi:timer-outline",
        value_fn=lambda d: _safe_int(d.get("uptime")),
    ),
    GenieAcsSensorDescription(
        key="firmware",
        translation_key="firmware",
        icon="mdi:cellphone-arrow-down",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("firmware"),
    ),
    GenieAcsSensorDescription(
        key="manufacturer",
        translation_key="manufacturer",
        icon="mdi:domain",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("manufacturer"),
    ),
    GenieAcsSensorDescription(
        key="model",
        translation_key="model",
        icon="mdi:router-wireless",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("model"),
    ),
    GenieAcsSensorDescription(
        key="serial",
        translation_key="serial",
        icon="mdi:identifier",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("serial"),
    ),
)


def _safe_int(value: Any) -> int | None:
    """Convert a value to int, returning None on failure."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GenieAcsConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GenieACS sensors from a config entry."""
    coordinator: GenieAcsCoordinator = entry.runtime_data
    entities: list[GenieAcsSensor] = [
        GenieAcsSensor(coordinator, device_id, description)
        for device_id in coordinator.data
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class GenieAcsSensor(GenieAcsEntity, SensorEntity):
    """A sensor that reads a value from a GenieACS device."""

    entity_description: GenieAcsSensorDescription

    def __init__(
        self,
        coordinator: GenieAcsCoordinator,
        device_id: str,
        description: GenieAcsSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        data = self.device_data
        if data is None:
            return None
        return self.entity_description.value_fn(data)
