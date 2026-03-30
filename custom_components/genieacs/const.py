"""Constants for the GenieACS integration."""

from typing import Final

DOMAIN: Final = "genieacs"

CONF_NBI_URL: Final = "nbi_url"

DEFAULT_NBI_URL: Final = "http://localhost:7557"
DEFAULT_SCAN_INTERVAL: Final = 60
ONLINE_THRESHOLD_SECONDS: Final = 300

# TR-069 parameter roots
TR181_ROOT: Final = "Device"
TR098_ROOT: Final = "InternetGatewayDevice"

# Common parameter suffixes (relative to root)
PARAM_MANUFACTURER: Final = "DeviceInfo.Manufacturer"
PARAM_MODEL: Final = "DeviceInfo.ModelName"
PARAM_SERIAL: Final = "DeviceInfo.SerialNumber"
PARAM_SOFTWARE_VERSION: Final = "DeviceInfo.SoftwareVersion"
PARAM_UPTIME: Final = "DeviceInfo.UpTime"
PARAM_WAN_IP: Final = (
    "WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.ExternalIPAddress"
)
