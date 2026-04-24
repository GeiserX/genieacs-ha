"""Tests for GenieACS constants."""

from __future__ import annotations

from custom_components.genieacs.const import (
    CONF_NBI_URL,
    DEFAULT_NBI_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ONLINE_THRESHOLD_SECONDS,
    PARAM_MANUFACTURER,
    PARAM_MODEL,
    PARAM_SERIAL,
    PARAM_SOFTWARE_VERSION,
    PARAM_UPTIME,
    PARAM_WAN_IP,
    TR098_ROOT,
    TR181_ROOT,
)


def test_domain() -> None:
    assert DOMAIN == "genieacs"


def test_conf_nbi_url() -> None:
    assert CONF_NBI_URL == "nbi_url"


def test_default_nbi_url() -> None:
    assert DEFAULT_NBI_URL == "http://localhost:7557"


def test_default_scan_interval() -> None:
    assert DEFAULT_SCAN_INTERVAL == 60


def test_online_threshold() -> None:
    assert ONLINE_THRESHOLD_SECONDS == 300


def test_tr181_root() -> None:
    assert TR181_ROOT == "Device"


def test_tr098_root() -> None:
    assert TR098_ROOT == "InternetGatewayDevice"


def test_param_manufacturer() -> None:
    assert PARAM_MANUFACTURER == "DeviceInfo.Manufacturer"


def test_param_model() -> None:
    assert PARAM_MODEL == "DeviceInfo.ModelName"


def test_param_serial() -> None:
    assert PARAM_SERIAL == "DeviceInfo.SerialNumber"


def test_param_software_version() -> None:
    assert PARAM_SOFTWARE_VERSION == "DeviceInfo.SoftwareVersion"


def test_param_uptime() -> None:
    assert PARAM_UPTIME == "DeviceInfo.UpTime"


def test_param_wan_ip() -> None:
    assert "WANIPConnection" in PARAM_WAN_IP
    assert "ExternalIPAddress" in PARAM_WAN_IP
