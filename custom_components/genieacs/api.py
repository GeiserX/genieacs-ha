"""Async HTTP client for the GenieACS NBI REST API."""

from __future__ import annotations

import json
import logging
from typing import Any

import aiohttp

from .const import (
    PARAM_MANUFACTURER,
    PARAM_MODEL,
    PARAM_SERIAL,
    PARAM_SOFTWARE_VERSION,
    PARAM_UPTIME,
    PARAM_WAN_IP,
    TR098_ROOT,
    TR181_ROOT,
)

_LOGGER = logging.getLogger(__name__)

DEVICE_PROJECTION = (
    "_id,_lastInform,_registered,_tags,"
    "Device.DeviceInfo,InternetGatewayDevice.DeviceInfo,"
    "Device.WANDevice,InternetGatewayDevice.WANDevice"
)


class GenieAcsError(Exception):
    """Base exception for GenieACS errors."""


class GenieAcsConnectionError(GenieAcsError):
    """Raised when the NBI is unreachable."""


class GenieAcsAuthError(GenieAcsError):
    """Raised on authentication failure (HTTP 401)."""


class GenieAcsApiClient:
    """Async client for the GenieACS NBI."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        nbi_url: str,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._nbi_url = nbi_url.rstrip("/")
        self._auth: aiohttp.BasicAuth | None = None
        if username and password:
            self._auth = aiohttp.BasicAuth(username, password)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def async_test_connection(self) -> bool:
        """Test the connection to the NBI by fetching one device ID."""
        await self._request("GET", "/devices/", params={"projection": "_id", "limit": "1"})
        return True

    async def async_get_devices(self) -> list[dict[str, Any]]:
        """Fetch all devices with projected fields."""
        raw: list[dict[str, Any]] = await self._request(
            "GET", "/devices/", params={"projection": DEVICE_PROJECTION}
        )
        return [self._normalize_device(d) for d in raw]

    async def async_get_device(self, device_id: str) -> dict[str, Any]:
        """Fetch a single device by its _id."""
        query = json.dumps({"_id": device_id})
        raw: list[dict[str, Any]] = await self._request(
            "GET", "/devices/", params={"query": query, "projection": DEVICE_PROJECTION}
        )
        if not raw:
            raise GenieAcsError(f"Device {device_id} not found")
        return self._normalize_device(raw[0])

    async def async_reboot_device(self, device_id: str) -> None:
        """Send a reboot task to a device."""
        await self._request(
            "POST",
            f"/devices/{device_id}/tasks",
            params={"connection_request": "", "timeout": "3000"},
            json_data={"name": "reboot"},
        )

    async def async_refresh_device(self, device_id: str) -> None:
        """Trigger a getParameterValues task to refresh device data."""
        root = "Device."  # will be tried first; GenieACS ignores unknown paths gracefully
        await self._request(
            "POST",
            f"/devices/{device_id}/tasks",
            params={"connection_request": "", "timeout": "3000"},
            json_data={
                "name": "getParameterValues",
                "parameterNames": [f"{root}DeviceInfo.", f"InternetGatewayDevice.DeviceInfo."],
            },
        )

    # ------------------------------------------------------------------
    # Parameter helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_param(device: dict[str, Any], suffix: str) -> Any | None:
        """Retrieve a TR-069 parameter value checking both TR-181 and TR-098 roots."""
        for root in (TR181_ROOT, TR098_ROOT):
            parts = f"{root}.{suffix}".split(".")
            node: Any = device
            for part in parts:
                if isinstance(node, dict):
                    node = node.get(part)
                else:
                    node = None
                    break
            if node is None:
                continue
            if isinstance(node, dict) and "_value" in node:
                return node["_value"]
            return node
        return None

    def _normalize_device(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Convert raw GenieACS device data into a flat dict."""
        device_id: str = raw.get("_id", "unknown")
        manufacturer = self._get_param(raw, PARAM_MANUFACTURER)
        model = self._get_param(raw, PARAM_MODEL)
        serial = self._get_param(raw, PARAM_SERIAL)
        firmware = self._get_param(raw, PARAM_SOFTWARE_VERSION)
        uptime = self._get_param(raw, PARAM_UPTIME)
        wan_ip = self._get_param(raw, PARAM_WAN_IP)
        last_inform = raw.get("_lastInform")

        return {
            "device_id": device_id,
            "manufacturer": manufacturer,
            "model": model,
            "serial": serial,
            "firmware": firmware,
            "uptime": uptime,
            "wan_ip": wan_ip,
            "last_inform": last_inform,
            "raw": raw,
        }

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> Any:
        """Execute an HTTP request against the NBI."""
        url = f"{self._nbi_url}{path}"
        try:
            async with self._session.request(
                method,
                url,
                params=params,
                json=json_data,
                auth=self._auth,
            ) as resp:
                if resp.status == 401:
                    raise GenieAcsAuthError("Invalid credentials for GenieACS NBI")
                resp.raise_for_status()
                if resp.content_type == "application/json":
                    return await resp.json()
                text = await resp.text()
                if text:
                    return json.loads(text)
                return None
        except GenieAcsAuthError:
            raise
        except aiohttp.ClientError as err:
            raise GenieAcsConnectionError(
                f"Error communicating with GenieACS NBI at {url}: {err}"
            ) from err
