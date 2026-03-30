"""Base entity for GenieACS devices."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GenieAcsCoordinator


class GenieAcsEntity(CoordinatorEntity[GenieAcsCoordinator]):
    """Base class for all GenieACS entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GenieAcsCoordinator,
        device_id: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._device_id = device_id

    @property
    def device_data(self) -> dict[str, Any] | None:
        """Return the current device data from the coordinator."""
        return self.coordinator.data.get(self._device_id)

    @property
    def available(self) -> bool:
        """Entity is available when the coordinator has data for this device."""
        return super().available and self.device_data is not None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for the HA device registry."""
        data = self.device_data or {}
        manufacturer = data.get("manufacturer")
        model = data.get("model")
        name = (
            f"{manufacturer} {model}"
            if manufacturer and model
            else self._device_id
        )
        nbi_url: str = self.coordinator.client._nbi_url
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=name,
            manufacturer=manufacturer,
            model=model,
            sw_version=data.get("firmware"),
            configuration_url=nbi_url,
        )
