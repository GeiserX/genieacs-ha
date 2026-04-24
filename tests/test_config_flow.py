"""Tests for the GenieACS config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.genieacs.api import (
    GenieAcsApiClient,
    GenieAcsAuthError,
    GenieAcsConnectionError,
)
from custom_components.genieacs.config_flow import (
    STEP_USER_DATA_SCHEMA,
    GenieAcsConfigFlow,
)
from custom_components.genieacs.const import (
    CONF_NBI_URL,
    DEFAULT_NBI_URL,
    DOMAIN,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_domain_constant() -> None:
    """Test the domain is correctly defined."""
    assert DOMAIN == "genieacs"


def test_default_nbi_url() -> None:
    """Test the default NBI URL."""
    assert DEFAULT_NBI_URL == "http://localhost:7557"


def test_config_flow_version() -> None:
    """Test config flow version is 1."""
    assert GenieAcsConfigFlow.VERSION == 1


def test_config_flow_domain() -> None:
    """Test config flow domain matches."""
    assert GenieAcsConfigFlow.domain == DOMAIN


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def test_data_schema_has_nbi_url() -> None:
    """Test that STEP_USER_DATA_SCHEMA includes nbi_url."""
    keys = [str(k) for k in STEP_USER_DATA_SCHEMA.schema]
    assert any("nbi_url" in k for k in keys)


# ---------------------------------------------------------------------------
# async_step_user - no input (shows form)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_step_user_no_input_shows_form() -> None:
    """Test that async_step_user shows a form when no input."""
    flow = GenieAcsConfigFlow()
    flow.hass = MagicMock()

    result = await flow.async_step_user(user_input=None)
    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert result["errors"] == {}


# ---------------------------------------------------------------------------
# async_step_user - successful connection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_step_user_success() -> None:
    """Test successful config flow creates an entry."""
    flow = GenieAcsConfigFlow()
    flow.hass = MagicMock()

    with patch(
        "custom_components.genieacs.config_flow.async_get_clientsession",
        return_value=MagicMock(),
    ), patch(
        "custom_components.genieacs.config_flow.GenieAcsApiClient",
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.async_test_connection = AsyncMock(return_value=True)
        mock_client_cls.return_value = mock_client

        result = await flow.async_step_user(user_input={
            CONF_NBI_URL: "http://genieacs:7557/",
            "username": "admin",
            "password": "secret",
        })

    assert result["type"] == "create_entry"
    assert result["title"] == "GenieACS (http://genieacs:7557)"
    assert result["data"][CONF_NBI_URL] == "http://genieacs:7557"


# ---------------------------------------------------------------------------
# async_step_user - auth error
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_step_user_auth_error() -> None:
    """Test that auth error shows invalid_auth."""
    flow = GenieAcsConfigFlow()
    flow.hass = MagicMock()

    with patch(
        "custom_components.genieacs.config_flow.async_get_clientsession",
        return_value=MagicMock(),
    ), patch(
        "custom_components.genieacs.config_flow.GenieAcsApiClient",
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.async_test_connection = AsyncMock(side_effect=GenieAcsAuthError("bad"))
        mock_client_cls.return_value = mock_client

        result = await flow.async_step_user(user_input={
            CONF_NBI_URL: "http://genieacs:7557",
        })

    assert result["type"] == "form"
    assert result["errors"] == {"base": "invalid_auth"}


# ---------------------------------------------------------------------------
# async_step_user - connection error
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_step_user_connection_error() -> None:
    """Test that connection error shows cannot_connect."""
    flow = GenieAcsConfigFlow()
    flow.hass = MagicMock()

    with patch(
        "custom_components.genieacs.config_flow.async_get_clientsession",
        return_value=MagicMock(),
    ), patch(
        "custom_components.genieacs.config_flow.GenieAcsApiClient",
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.async_test_connection = AsyncMock(
            side_effect=GenieAcsConnectionError("down")
        )
        mock_client_cls.return_value = mock_client

        result = await flow.async_step_user(user_input={
            CONF_NBI_URL: "http://genieacs:7557",
        })

    assert result["type"] == "form"
    assert result["errors"] == {"base": "cannot_connect"}


# ---------------------------------------------------------------------------
# async_step_user - unknown error
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_step_user_unknown_error() -> None:
    """Test that unexpected error shows unknown."""
    flow = GenieAcsConfigFlow()
    flow.hass = MagicMock()

    with patch(
        "custom_components.genieacs.config_flow.async_get_clientsession",
        return_value=MagicMock(),
    ), patch(
        "custom_components.genieacs.config_flow.GenieAcsApiClient",
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.async_test_connection = AsyncMock(
            side_effect=RuntimeError("boom")
        )
        mock_client_cls.return_value = mock_client

        result = await flow.async_step_user(user_input={
            CONF_NBI_URL: "http://genieacs:7557",
        })

    assert result["type"] == "form"
    assert result["errors"] == {"base": "unknown"}


# ---------------------------------------------------------------------------
# URL normalization
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_step_user_strips_trailing_slash() -> None:
    """Test that the trailing slash is stripped from the URL in data."""
    flow = GenieAcsConfigFlow()
    flow.hass = MagicMock()

    with patch(
        "custom_components.genieacs.config_flow.async_get_clientsession",
        return_value=MagicMock(),
    ), patch(
        "custom_components.genieacs.config_flow.GenieAcsApiClient",
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.async_test_connection = AsyncMock(return_value=True)
        mock_client_cls.return_value = mock_client

        result = await flow.async_step_user(user_input={
            CONF_NBI_URL: "http://genieacs:7557///",
        })

    assert result["data"][CONF_NBI_URL] == "http://genieacs:7557"
