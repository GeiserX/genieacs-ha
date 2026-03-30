"""Button platform for GenieACS."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import GenieAcsConfigEntry
from .api import GenieAcsApiClient
from .coordinator import GenieAcsCoordinator
from .entity import GenieAcsEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class GenieAcsButtonDescription(ButtonEntityDescription):
    """Describe a GenieACS button entity."""

    press_fn: Callable[[GenieAcsApiClient, str], Coroutine[Any, Any, None]]


BUTTON_DESCRIPTIONS: tuple[GenieAcsButtonDescription, ...] = (
    GenieAcsButtonDescription(
        key="reboot",
        translation_key="reboot",
        device_class=ButtonDeviceClass.RESTART,
        icon="mdi:restart",
        press_fn=lambda client, did: client.async_reboot_device(did),
    ),
    GenieAcsButtonDescription(
        key="refresh",
        translation_key="refresh",
        icon="mdi:refresh",
        entity_category=EntityCategory.DIAGNOSTIC,
        press_fn=lambda client, did: client.async_refresh_device(did),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GenieAcsConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GenieACS buttons from a config entry."""
    coordinator: GenieAcsCoordinator = entry.runtime_data
    entities: list[GenieAcsButton] = [
        GenieAcsButton(coordinator, device_id, description)
        for device_id in coordinator.data
        for description in BUTTON_DESCRIPTIONS
    ]
    async_add_entities(entities)


class GenieAcsButton(GenieAcsEntity, ButtonEntity):
    """A button that triggers an action on a GenieACS device."""

    entity_description: GenieAcsButtonDescription

    def __init__(
        self,
        coordinator: GenieAcsCoordinator,
        device_id: str,
        description: GenieAcsButtonDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}_{description.key}"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.entity_description.press_fn(
            self.coordinator.client, self._device_id
        )
        await self.coordinator.async_request_refresh()
