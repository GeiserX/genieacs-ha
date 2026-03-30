"""Config flow for GenieACS integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GenieAcsApiClient, GenieAcsAuthError, GenieAcsConnectionError
from .const import CONF_NBI_URL, DEFAULT_NBI_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NBI_URL, default=DEFAULT_NBI_URL): str,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
    }
)


class GenieAcsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GenieACS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step: NBI URL + credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            nbi_url = user_input[CONF_NBI_URL].rstrip("/")
            user_input[CONF_NBI_URL] = nbi_url

            # Deduplicate by NBI URL
            await self.async_set_unique_id(nbi_url)
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = GenieAcsApiClient(
                session=session,
                nbi_url=nbi_url,
                username=user_input.get(CONF_USERNAME),
                password=user_input.get(CONF_PASSWORD),
            )

            try:
                await client.async_test_connection()
            except GenieAcsAuthError:
                errors["base"] = "invalid_auth"
            except GenieAcsConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during GenieACS connection test")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"GenieACS ({nbi_url})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
