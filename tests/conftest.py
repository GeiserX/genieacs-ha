"""Common fixtures and HA mocks for GenieACS tests."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock


def _make_ha_mocks():
    """Create minimal mocks for homeassistant modules so imports work."""
    mods = {}

    ha = MagicMock()
    mods["homeassistant"] = ha
    mods["homeassistant.core"] = MagicMock()

    const = ModuleType("homeassistant.const")
    const.CONF_PASSWORD = "password"
    const.CONF_USERNAME = "username"
    const.Platform = MagicMock()
    const.Platform.BINARY_SENSOR = "binary_sensor"
    const.Platform.BUTTON = "button"
    const.Platform.SENSOR = "sensor"
    const.EntityCategory = MagicMock()
    const.EntityCategory.DIAGNOSTIC = "diagnostic"
    const.UnitOfTime = MagicMock()
    const.UnitOfTime.SECONDS = "s"
    mods["homeassistant.const"] = const

    mods["homeassistant.config_entries"] = MagicMock()

    for mod_name in [
        "homeassistant.helpers",
        "homeassistant.helpers.aiohttp_client",
        "homeassistant.helpers.device_registry",
        "homeassistant.helpers.entity_platform",
        "homeassistant.helpers.update_coordinator",
    ]:
        mods[mod_name] = MagicMock()

    sensor_mod = MagicMock()
    sensor_mod.SensorDeviceClass = MagicMock()
    sensor_mod.SensorDeviceClass.DURATION = "duration"
    sensor_mod.SensorStateClass = MagicMock()
    mods["homeassistant.components"] = MagicMock()
    mods["homeassistant.components.sensor"] = sensor_mod
    mods["homeassistant.components.binary_sensor"] = MagicMock()
    mods["homeassistant.components.button"] = MagicMock()
    mods["homeassistant.data_entry_flow"] = MagicMock()

    return mods


_ha_mocks = _make_ha_mocks()
for name, mod in _ha_mocks.items():
    sys.modules[name] = mod


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
