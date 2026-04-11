"""Tests for the GenieACS API client."""

from __future__ import annotations

import pytest
from aiohttp import ClientSession
from aiohttp.test_utils import TestServer
from aiohttp.web import Application, Request, Response, json_response

from custom_components.genieacs.api import (
    GenieAcsApiClient,
    GenieAcsAuthError,
    GenieAcsConnectionError,
    GenieAcsError,
)

from .conftest import MOCK_DEVICE_RAW


@pytest.mark.asyncio
async def test_test_connection_success() -> None:
    """Test successful connection test."""
    app = Application()

    async def handle(request: Request) -> Response:
        return json_response([{"_id": "test"}])

    app.router.add_get("/devices/", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            result = await client.async_test_connection()
            assert result is True


@pytest.mark.asyncio
async def test_test_connection_auth_error() -> None:
    """Test 401 raises GenieAcsAuthError."""
    app = Application()

    async def handle(request: Request) -> Response:
        return Response(status=401)

    app.router.add_get("/devices/", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            with pytest.raises(GenieAcsAuthError):
                await client.async_test_connection()


@pytest.mark.asyncio
async def test_connection_error() -> None:
    """Test unreachable server raises GenieAcsConnectionError."""
    async with ClientSession() as session:
        client = GenieAcsApiClient(session, "http://127.0.0.1:1")
        with pytest.raises(GenieAcsConnectionError):
            await client.async_test_connection()


@pytest.mark.asyncio
async def test_get_devices_normalizes() -> None:
    """Test that get_devices normalizes raw device data."""
    app = Application()

    async def handle(request: Request) -> Response:
        return json_response([MOCK_DEVICE_RAW])

    app.router.add_get("/devices/", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            devices = await client.async_get_devices()
            assert len(devices) == 1
            d = devices[0]
            assert d["device_id"] == "001122-TestRouter-AABBCC"
            assert d["manufacturer"] == "TestMfg"
            assert d["model"] == "TestModel"
            assert d["serial"] == "AABBCC"
            assert d["firmware"] == "1.2.3"
            assert d["uptime"] == 86400
            assert d["wan_ip"] == "1.2.3.4"


@pytest.mark.asyncio
async def test_get_device_not_found() -> None:
    """Test that get_device raises on empty result."""
    app = Application()

    async def handle(request: Request) -> Response:
        return json_response([])

    app.router.add_get("/devices/", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            with pytest.raises(GenieAcsError, match="not found"):
                await client.async_get_device("nonexistent")


def test_get_param_tr181() -> None:
    """Test parameter extraction with TR-181 root."""
    result = GenieAcsApiClient._get_param(MOCK_DEVICE_RAW, "DeviceInfo.Manufacturer")
    assert result == "TestMfg"


def test_get_param_missing() -> None:
    """Test parameter extraction for a missing param."""
    result = GenieAcsApiClient._get_param({}, "DeviceInfo.Manufacturer")
    assert result is None


def test_get_param_uptime() -> None:
    """Test uptime parameter extraction."""
    result = GenieAcsApiClient._get_param(MOCK_DEVICE_RAW, "DeviceInfo.UpTime")
    assert result == 86400


def test_get_param_wan_ip() -> None:
    """Test WAN IP parameter extraction through nested path."""
    from custom_components.genieacs.const import PARAM_WAN_IP
    result = GenieAcsApiClient._get_param(MOCK_DEVICE_RAW, PARAM_WAN_IP)
    assert result == "1.2.3.4"


@pytest.mark.asyncio
async def test_reboot_device() -> None:
    """Test reboot sends a POST task."""
    app = Application()
    received = {}

    async def handle(request: Request) -> Response:
        received["data"] = await request.json()
        return json_response({})

    app.router.add_post("/devices/{device_id}/tasks", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            await client.async_reboot_device("test-device")
            assert received["data"]["name"] == "reboot"


@pytest.mark.asyncio
async def test_refresh_device() -> None:
    """Test refresh sends a getParameterValues task."""
    app = Application()
    received = {}

    async def handle(request: Request) -> Response:
        received["data"] = await request.json()
        return json_response({})

    app.router.add_post("/devices/{device_id}/tasks", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            await client.async_refresh_device("test-device")
            assert received["data"]["name"] == "getParameterValues"


@pytest.mark.asyncio
async def test_get_devices_empty() -> None:
    """Test get_devices with no devices returns empty list."""
    app = Application()

    async def handle(request: Request) -> Response:
        return json_response([])

    app.router.add_get("/devices/", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            devices = await client.async_get_devices()
            assert devices == []
