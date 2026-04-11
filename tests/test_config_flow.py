"""Tests for the GenieACS config flow logic."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from custom_components.genieacs.api import (
    GenieAcsAuthError,
    GenieAcsConnectionError,
)
from custom_components.genieacs.const import (
    CONF_NBI_URL,
    DEFAULT_NBI_URL,
    DOMAIN,
)


def test_domain_constant() -> None:
    """Test the domain is correctly defined."""
    assert DOMAIN == "genieacs"


def test_default_nbi_url() -> None:
    """Test the default NBI URL."""
    assert DEFAULT_NBI_URL == "http://localhost:7557"


@pytest.mark.asyncio
async def test_connection_error_detection() -> None:
    """Test that connection errors are detected during config validation."""
    from custom_components.genieacs.api import GenieAcsApiClient
    import aiohttp

    async with aiohttp.ClientSession() as session:
        client = GenieAcsApiClient(session, "http://127.0.0.1:1")
        with pytest.raises(GenieAcsConnectionError):
            await client.async_test_connection()


@pytest.mark.asyncio
async def test_url_trailing_slash_stripped() -> None:
    """Test that trailing slashes are stripped."""
    from custom_components.genieacs.api import GenieAcsApiClient
    import aiohttp

    async with aiohttp.ClientSession() as session:
        client = GenieAcsApiClient(session, "http://genieacs:7557/")
        assert client._nbi_url == "http://genieacs:7557"


@pytest.mark.asyncio
async def test_auth_setup() -> None:
    """Test that auth is configured when credentials are provided."""
    from custom_components.genieacs.api import GenieAcsApiClient
    import aiohttp

    async with aiohttp.ClientSession() as session:
        client = GenieAcsApiClient(
            session, "http://genieacs:7557", username="admin", password="secret"
        )
        assert client._auth is not None
        assert client._auth.login == "admin"


@pytest.mark.asyncio
async def test_no_auth_without_credentials() -> None:
    """Test that auth is None without credentials."""
    from custom_components.genieacs.api import GenieAcsApiClient
    import aiohttp

    async with aiohttp.ClientSession() as session:
        client = GenieAcsApiClient(session, "http://genieacs:7557")
        assert client._auth is None
