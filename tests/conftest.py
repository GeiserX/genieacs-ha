"""Common fixtures and HA mocks for GenieACS tests."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from types import ModuleType
from typing import Any
from unittest.mock import AsyncMock, MagicMock, PropertyMock


# ---------------------------------------------------------------------------
# Minimal Home Assistant shims so that every import inside
# custom_components.genieacs.* resolves without the real HA package.
# ---------------------------------------------------------------------------

def _make_ha_mocks() -> dict[str, Any]:
    """Create minimal mocks for homeassistant modules so imports work."""
    mods: dict[str, Any] = {}

    # -- homeassistant (top-level) --
    ha = MagicMock()
    mods["homeassistant"] = ha

    # -- homeassistant.core --
    core = ModuleType("homeassistant.core")
    core.HomeAssistant = MagicMock  # type: ignore[attr-defined]
    mods["homeassistant.core"] = core

    # -- homeassistant.const --
    const = ModuleType("homeassistant.const")
    const.CONF_PASSWORD = "password"  # type: ignore[attr-defined]
    const.CONF_USERNAME = "username"  # type: ignore[attr-defined]

    class _Platform:
        BINARY_SENSOR = "binary_sensor"
        BUTTON = "button"
        SENSOR = "sensor"

    const.Platform = _Platform  # type: ignore[attr-defined]

    class _EntityCategory:
        DIAGNOSTIC = "diagnostic"

    const.EntityCategory = _EntityCategory  # type: ignore[attr-defined]

    class _UnitOfTime:
        SECONDS = "s"

    const.UnitOfTime = _UnitOfTime  # type: ignore[attr-defined]
    mods["homeassistant.const"] = const

    # -- homeassistant.config_entries --
    config_entries_mod = ModuleType("homeassistant.config_entries")

    class _ConfigEntry:
        """Minimal ConfigEntry stub."""

        def __init__(self, **kwargs: Any) -> None:
            self.data = kwargs.get("data", {})
            self.runtime_data: Any = None
            self.entry_id = kwargs.get("entry_id", "test_entry_id")

        def __class_getitem__(cls, item: Any) -> Any:
            return cls

    class _ConfigFlow:
        """Minimal ConfigFlow stub."""
        domain: str = ""
        VERSION: int = 1

        def __init_subclass__(cls, domain: str = "", **kwargs: Any) -> None:
            super().__init_subclass__(**kwargs)
            cls.domain = domain

        def __init__(self) -> None:
            self.hass: Any = None

        async def async_set_unique_id(self, uid: str) -> None:
            pass

        def _abort_if_unique_id_configured(self) -> None:
            pass

        def async_create_entry(self, *, title: str, data: dict) -> dict:
            return {"type": "create_entry", "title": title, "data": data}

        def async_show_form(self, *, step_id: str, data_schema: Any, errors: dict) -> dict:
            return {"type": "form", "step_id": step_id, "errors": errors}

    class _ConfigFlowResult(dict):
        pass

    config_entries_mod.ConfigEntry = _ConfigEntry  # type: ignore[attr-defined]
    config_entries_mod.ConfigFlow = _ConfigFlow  # type: ignore[attr-defined]
    config_entries_mod.ConfigFlowResult = _ConfigFlowResult  # type: ignore[attr-defined]
    mods["homeassistant.config_entries"] = config_entries_mod

    # -- homeassistant.helpers --
    mods["homeassistant.helpers"] = MagicMock()

    # -- homeassistant.helpers.aiohttp_client --
    aiohttp_client_mod = ModuleType("homeassistant.helpers.aiohttp_client")
    aiohttp_client_mod.async_get_clientsession = MagicMock()  # type: ignore[attr-defined]
    mods["homeassistant.helpers.aiohttp_client"] = aiohttp_client_mod

    # -- homeassistant.helpers.device_registry --
    device_reg_mod = ModuleType("homeassistant.helpers.device_registry")

    class _DeviceInfo(dict):
        """Minimal DeviceInfo stub."""

        def __init__(self, **kwargs: Any) -> None:
            super().__init__(**kwargs)
            for k, v in kwargs.items():
                setattr(self, k, v)

    device_reg_mod.DeviceInfo = _DeviceInfo  # type: ignore[attr-defined]
    mods["homeassistant.helpers.device_registry"] = device_reg_mod

    # -- homeassistant.helpers.entity_platform --
    entity_platform_mod = ModuleType("homeassistant.helpers.entity_platform")
    entity_platform_mod.AddEntitiesCallback = Any  # type: ignore[attr-defined]
    mods["homeassistant.helpers.entity_platform"] = entity_platform_mod

    # -- homeassistant.helpers.update_coordinator --
    update_coord_mod = ModuleType("homeassistant.helpers.update_coordinator")

    class _DataUpdateCoordinator:
        """Minimal DataUpdateCoordinator stub."""

        def __init__(self, hass: Any, logger: Any, *, name: str, update_interval: Any) -> None:
            self.hass = hass
            self.logger = logger
            self.name = name
            self.update_interval = update_interval
            self.data: Any = {}
            self.last_update_success = True

        def __class_getitem__(cls, item: Any) -> Any:
            return cls

        async def async_config_entry_first_refresh(self) -> None:
            self.data = await self._async_update_data()

        async def async_request_refresh(self) -> None:
            self.data = await self._async_update_data()

        async def _async_update_data(self) -> Any:
            raise NotImplementedError

    class _UpdateFailed(Exception):
        pass

    class _CoordinatorEntity:
        """Minimal CoordinatorEntity stub."""

        def __init__(self, coordinator: Any) -> None:
            self.coordinator = coordinator

        def __class_getitem__(cls, item: Any) -> Any:
            return cls

        @property
        def available(self) -> bool:
            return self.coordinator.last_update_success

    update_coord_mod.DataUpdateCoordinator = _DataUpdateCoordinator  # type: ignore[attr-defined]
    update_coord_mod.UpdateFailed = _UpdateFailed  # type: ignore[attr-defined]
    update_coord_mod.CoordinatorEntity = _CoordinatorEntity  # type: ignore[attr-defined]
    mods["homeassistant.helpers.update_coordinator"] = update_coord_mod

    # -- homeassistant.components.* --
    mods["homeassistant.components"] = MagicMock()

    # -- homeassistant.components.binary_sensor --
    bs_mod = ModuleType("homeassistant.components.binary_sensor")

    class _BinarySensorDeviceClass:
        CONNECTIVITY = "connectivity"

    class _BinarySensorEntity:
        _attr_device_class: Any = None
        _attr_translation_key: str | None = None
        _attr_unique_id: str | None = None
        _attr_has_entity_name: bool = False

        @property
        def is_on(self) -> bool | None:
            return None

    bs_mod.BinarySensorDeviceClass = _BinarySensorDeviceClass  # type: ignore[attr-defined]
    bs_mod.BinarySensorEntity = _BinarySensorEntity  # type: ignore[attr-defined]
    mods["homeassistant.components.binary_sensor"] = bs_mod

    # -- homeassistant.components.button --
    btn_mod = ModuleType("homeassistant.components.button")

    class _ButtonDeviceClass:
        RESTART = "restart"

    @dataclass(frozen=True, kw_only=True)
    class _ButtonEntityDescription:
        key: str = ""
        translation_key: str | None = None
        device_class: Any = None
        icon: str | None = None
        entity_category: Any = None
        name: str | None = None
        has_entity_name: bool = False

    class _ButtonEntity:
        _attr_unique_id: str | None = None
        _attr_has_entity_name: bool = False
        entity_description: Any = None

        async def async_press(self) -> None:
            pass

    btn_mod.ButtonDeviceClass = _ButtonDeviceClass  # type: ignore[attr-defined]
    btn_mod.ButtonEntityDescription = _ButtonEntityDescription  # type: ignore[attr-defined]
    btn_mod.ButtonEntity = _ButtonEntity  # type: ignore[attr-defined]
    mods["homeassistant.components.button"] = btn_mod

    # -- homeassistant.components.sensor --
    sensor_mod = ModuleType("homeassistant.components.sensor")

    class _SensorDeviceClass:
        DURATION = "duration"

    @dataclass(frozen=True, kw_only=True)
    class _SensorEntityDescription:
        key: str = ""
        translation_key: str | None = None
        device_class: Any = None
        native_unit_of_measurement: str | None = None
        icon: str | None = None
        entity_category: Any = None
        name: str | None = None
        has_entity_name: bool = False
        state_class: Any = None
        suggested_display_precision: int | None = None

    class _SensorEntity:
        _attr_unique_id: str | None = None
        _attr_has_entity_name: bool = False
        entity_description: Any = None

        @property
        def native_value(self) -> Any:
            return None

    class _SensorStateClass:
        MEASUREMENT = "measurement"

    sensor_mod.SensorDeviceClass = _SensorDeviceClass  # type: ignore[attr-defined]
    sensor_mod.SensorEntityDescription = _SensorEntityDescription  # type: ignore[attr-defined]
    sensor_mod.SensorEntity = _SensorEntity  # type: ignore[attr-defined]
    sensor_mod.SensorStateClass = _SensorStateClass  # type: ignore[attr-defined]
    mods["homeassistant.components.sensor"] = sensor_mod

    # -- homeassistant.data_entry_flow --
    mods["homeassistant.data_entry_flow"] = MagicMock()

    return mods


_ha_mocks = _make_ha_mocks()
for name, mod in _ha_mocks.items():
    sys.modules[name] = mod


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

MOCK_DEVICE_RAW = {
    "_id": "001122-TestRouter-AABBCC",
    "_lastInform": "2026-01-01T12:00:00.000Z",
    "Device": {
        "DeviceInfo": {
            "Manufacturer": {"_value": "TestMfg"},
            "ModelName": {"_value": "TestModel"},
            "SerialNumber": {"_value": "AABBCC"},
            "SoftwareVersion": {"_value": "1.2.3"},
            "UpTime": {"_value": 86400},
        },
        "WANDevice": {
            "1": {
                "WANConnectionDevice": {
                    "1": {
                        "WANIPConnection": {
                            "1": {
                                "ExternalIPAddress": {"_value": "1.2.3.4"}
                            }
                        }
                    }
                }
            }
        },
    },
}

MOCK_DEVICE_RAW_TR098 = {
    "_id": "TR098-Router-112233",
    "_lastInform": "2026-01-01T12:00:00.000Z",
    "InternetGatewayDevice": {
        "DeviceInfo": {
            "Manufacturer": {"_value": "OldMfg"},
            "ModelName": {"_value": "OldModel"},
            "SerialNumber": {"_value": "112233"},
            "SoftwareVersion": {"_value": "0.9.1"},
            "UpTime": {"_value": 3600},
        },
        "WANDevice": {
            "1": {
                "WANConnectionDevice": {
                    "1": {
                        "WANIPConnection": {
                            "1": {
                                "ExternalIPAddress": {"_value": "5.6.7.8"}
                            }
                        }
                    }
                }
            }
        },
    },
}

MOCK_DEVICE_NORMALIZED = {
    "device_id": "001122-TestRouter-AABBCC",
    "manufacturer": "TestMfg",
    "model": "TestModel",
    "serial": "AABBCC",
    "firmware": "1.2.3",
    "uptime": 86400,
    "wan_ip": "1.2.3.4",
    "last_inform": "2026-01-01T12:00:00.000Z",
    "raw": MOCK_DEVICE_RAW,
}

MOCK_DEVICE_NORMALIZED_TR098 = {
    "device_id": "TR098-Router-112233",
    "manufacturer": "OldMfg",
    "model": "OldModel",
    "serial": "112233",
    "firmware": "0.9.1",
    "uptime": 3600,
    "wan_ip": "5.6.7.8",
    "last_inform": "2026-01-01T12:00:00.000Z",
    "raw": MOCK_DEVICE_RAW_TR098,
}


def make_coordinator(
    devices: dict[str, dict] | None = None,
    client: Any = None,
) -> Any:
    """Create a mock coordinator with device data preloaded."""
    from custom_components.genieacs.coordinator import GenieAcsCoordinator

    if client is None:
        client = MagicMock()
        client.async_get_devices = AsyncMock(return_value=[])
        client._nbi_url = "http://genieacs:7557"

    hass = MagicMock()
    coordinator = GenieAcsCoordinator(hass, client)
    coordinator.data = devices if devices is not None else {
        MOCK_DEVICE_NORMALIZED["device_id"]: MOCK_DEVICE_NORMALIZED,
    }
    coordinator.last_update_success = True
    return coordinator
