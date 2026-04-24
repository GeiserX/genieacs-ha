"""Tests for the GenieACS API client."""

from __future__ import annotations

import json

import pytest
from aiohttp import BasicAuth, ClientSession
from aiohttp.test_utils import TestServer
from aiohttp.web import Application, Request, Response, json_response

from custom_components.genieacs.api import (
    GenieAcsApiClient,
    GenieAcsAuthError,
    GenieAcsConnectionError,
    GenieAcsError,
)

from .conftest import MOCK_DEVICE_RAW, MOCK_DEVICE_RAW_TR098


# ---------------------------------------------------------------------------
# Connection / auth
# ---------------------------------------------------------------------------

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
async def test_auth_header_sent() -> None:
    """Test that basic auth is sent when credentials are configured."""
    app = Application()
    received_auth: dict[str, str | None] = {"header": None}

    async def handle(request: Request) -> Response:
        received_auth["header"] = request.headers.get("Authorization")
        return json_response([{"_id": "x"}])

    app.router.add_get("/devices/", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(
                session, str(server.make_url("")), username="admin", password="secret"
            )
            await client.async_test_connection()
            assert received_auth["header"] is not None
            assert received_auth["header"].startswith("Basic ")


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_url_trailing_slash_stripped() -> None:
    """Test that trailing slashes are stripped."""
    async with ClientSession() as session:
        client = GenieAcsApiClient(session, "http://genieacs:7557/")
        assert client._nbi_url == "http://genieacs:7557"


@pytest.mark.asyncio
async def test_auth_setup_with_credentials() -> None:
    """Test that auth is configured when credentials are provided."""
    async with ClientSession() as session:
        client = GenieAcsApiClient(
            session, "http://genieacs:7557", username="admin", password="secret"
        )
        assert client._auth is not None
        assert client._auth.login == "admin"


@pytest.mark.asyncio
async def test_no_auth_without_credentials() -> None:
    """Test that auth is None without credentials."""
    async with ClientSession() as session:
        client = GenieAcsApiClient(session, "http://genieacs:7557")
        assert client._auth is None


@pytest.mark.asyncio
async def test_no_auth_with_empty_username() -> None:
    """Test that auth is None when username is empty string."""
    async with ClientSession() as session:
        client = GenieAcsApiClient(session, "http://x:7557", username="", password="pass")
        assert client._auth is None


@pytest.mark.asyncio
async def test_no_auth_with_empty_password() -> None:
    """Test that auth is None when password is empty string."""
    async with ClientSession() as session:
        client = GenieAcsApiClient(session, "http://x:7557", username="admin", password="")
        assert client._auth is None


# ---------------------------------------------------------------------------
# get_devices
# ---------------------------------------------------------------------------

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
            assert d["last_inform"] == "2026-01-01T12:00:00.000Z"
            assert d["raw"] == MOCK_DEVICE_RAW


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


@pytest.mark.asyncio
async def test_get_devices_multiple() -> None:
    """Test get_devices with multiple devices."""
    app = Application()

    async def handle(request: Request) -> Response:
        return json_response([MOCK_DEVICE_RAW, MOCK_DEVICE_RAW_TR098])

    app.router.add_get("/devices/", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            devices = await client.async_get_devices()
            assert len(devices) == 2
            assert devices[0]["device_id"] == "001122-TestRouter-AABBCC"
            assert devices[1]["device_id"] == "TR098-Router-112233"


@pytest.mark.asyncio
async def test_get_devices_sends_projection() -> None:
    """Test that get_devices sends the projection parameter."""
    app = Application()
    received_params: dict[str, str] = {}

    async def handle(request: Request) -> Response:
        received_params.update(request.query)
        return json_response([])

    app.router.add_get("/devices/", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            await client.async_get_devices()
            assert "projection" in received_params


# ---------------------------------------------------------------------------
# get_device
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_device_found() -> None:
    """Test fetching a single device by ID."""
    app = Application()

    async def handle(request: Request) -> Response:
        return json_response([MOCK_DEVICE_RAW])

    app.router.add_get("/devices/", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            device = await client.async_get_device("001122-TestRouter-AABBCC")
            assert device["device_id"] == "001122-TestRouter-AABBCC"


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


@pytest.mark.asyncio
async def test_get_device_sends_query() -> None:
    """Test that get_device sends a JSON query filter."""
    app = Application()
    received_params: dict[str, str] = {}

    async def handle(request: Request) -> Response:
        received_params.update(request.query)
        return json_response([MOCK_DEVICE_RAW])

    app.router.add_get("/devices/", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            await client.async_get_device("my-device")
            assert "query" in received_params
            parsed = json.loads(received_params["query"])
            assert parsed == {"_id": "my-device"}


# ---------------------------------------------------------------------------
# reboot / refresh
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_reboot_device() -> None:
    """Test reboot sends a POST task."""
    app = Application()
    received: dict[str, Any] = {}

    async def handle(request: Request) -> Response:
        received["data"] = await request.json()
        received["params"] = dict(request.query)
        return json_response({})

    app.router.add_post("/devices/{device_id}/tasks", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            await client.async_reboot_device("test-device")
            assert received["data"]["name"] == "reboot"
            assert "connection_request" in received["params"]


@pytest.mark.asyncio
async def test_refresh_device() -> None:
    """Test refresh sends a getParameterValues task."""
    app = Application()
    received: dict[str, Any] = {}

    async def handle(request: Request) -> Response:
        received["data"] = await request.json()
        return json_response({})

    app.router.add_post("/devices/{device_id}/tasks", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            await client.async_refresh_device("test-device")
            assert received["data"]["name"] == "getParameterValues"
            assert isinstance(received["data"]["parameterNames"], list)


# ---------------------------------------------------------------------------
# _get_param
# ---------------------------------------------------------------------------

def test_get_param_tr181() -> None:
    """Test parameter extraction with TR-181 root."""
    result = GenieAcsApiClient._get_param(MOCK_DEVICE_RAW, "DeviceInfo.Manufacturer")
    assert result == "TestMfg"


def test_get_param_tr098() -> None:
    """Test parameter extraction with TR-098 root."""
    result = GenieAcsApiClient._get_param(MOCK_DEVICE_RAW_TR098, "DeviceInfo.Manufacturer")
    assert result == "OldMfg"


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


def test_get_param_non_dict_node() -> None:
    """Test _get_param returns None when encountering a non-dict node."""
    raw = {"Device": {"DeviceInfo": "not_a_dict"}}
    result = GenieAcsApiClient._get_param(raw, "DeviceInfo.Manufacturer")
    assert result is None


def test_get_param_raw_value_without_value_key() -> None:
    """Test _get_param returns the node directly if no _value key."""
    raw = {"Device": {"DeviceInfo": {"Manufacturer": "DirectValue"}}}
    result = GenieAcsApiClient._get_param(raw, "DeviceInfo.Manufacturer")
    assert result == "DirectValue"


# ---------------------------------------------------------------------------
# _normalize_device
# ---------------------------------------------------------------------------

def test_normalize_device_minimal() -> None:
    """Test normalization of a device with minimal data."""
    raw = {"_id": "bare-device"}
    client = GenieAcsApiClient.__new__(GenieAcsApiClient)
    result = client._normalize_device(raw)
    assert result["device_id"] == "bare-device"
    assert result["manufacturer"] is None
    assert result["model"] is None
    assert result["serial"] is None
    assert result["firmware"] is None
    assert result["uptime"] is None
    assert result["wan_ip"] is None
    assert result["last_inform"] is None


def test_normalize_device_unknown_id() -> None:
    """Test normalization when _id is missing."""
    raw = {}
    client = GenieAcsApiClient.__new__(GenieAcsApiClient)
    result = client._normalize_device(raw)
    assert result["device_id"] == "unknown"


# ---------------------------------------------------------------------------
# _request edge cases
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_request_plain_text_json() -> None:
    """Test _request parses JSON from text/plain content type."""
    app = Application()

    async def handle(request: Request) -> Response:
        return Response(
            text='[{"_id": "text-json"}]',
            content_type="text/plain",
        )

    app.router.add_get("/devices/", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            result = await client._request("GET", "/devices/")
            assert result == [{"_id": "text-json"}]


@pytest.mark.asyncio
async def test_request_empty_response() -> None:
    """Test _request returns None for empty body."""
    app = Application()

    async def handle(request: Request) -> Response:
        return Response(text="", content_type="text/plain")

    app.router.add_get("/empty", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            result = await client._request("GET", "/empty")
            assert result is None


@pytest.mark.asyncio
async def test_request_http_500() -> None:
    """Test that a 500 error is wrapped as GenieAcsConnectionError."""
    app = Application()

    async def handle(request: Request) -> Response:
        return Response(status=500)

    app.router.add_get("/fail", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = GenieAcsApiClient(session, str(server.make_url("")))
            with pytest.raises(GenieAcsConnectionError):
                await client._request("GET", "/fail")


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------

def test_exception_hierarchy() -> None:
    """Test that specific errors inherit from GenieAcsError."""
    assert issubclass(GenieAcsConnectionError, GenieAcsError)
    assert issubclass(GenieAcsAuthError, GenieAcsError)
    assert issubclass(GenieAcsError, Exception)
