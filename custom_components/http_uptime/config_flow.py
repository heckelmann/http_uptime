"""Config flow for HTTP Uptime Monitor integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_ENDPOINTS,
    CONF_EXPECTED_STATUS,
    CONF_HEADERS,
    CONF_METHOD,
    CONF_TIMEOUT,
    CONF_UPDATE_INTERVAL,
    CONF_VERIFY_SSL,
    DEFAULT_EXPECTED_STATUS,
    DEFAULT_METHOD,
    DEFAULT_TIMEOUT,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_URL): str,
        vol.Optional(CONF_METHOD, default=DEFAULT_METHOD): vol.In(
            ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
        ),
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=300)
        ),
        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=3600)
        ),
        vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
        vol.Optional(CONF_EXPECTED_STATUS, default=DEFAULT_EXPECTED_STATUS): str,
        vol.Optional(CONF_HEADERS, default=""): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    # Parse expected status codes
    try:
        expected_status = [int(x.strip()) for x in data[CONF_EXPECTED_STATUS].split(",")]
    except ValueError:
        expected_status = DEFAULT_EXPECTED_STATUS
    
    # Parse headers
    headers = {}
    if data.get(CONF_HEADERS):
        try:
            for line in data[CONF_HEADERS].split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.strip()] = value.strip()
        except Exception:
            headers = {}

    # Test the connection
    timeout = aiohttp.ClientTimeout(total=data[CONF_TIMEOUT])
    connector = aiohttp.TCPConnector(verify_ssl=data[CONF_VERIFY_SSL])
    
    try:
        async with aiohttp.ClientSession(
            timeout=timeout, connector=connector, headers=headers
        ) as session:
            async with session.request(
                data[CONF_METHOD], data[CONF_URL]
            ) as response:
                if response.status not in expected_status:
                    _LOGGER.warning(
                        "Unexpected status code %s for %s", 
                        response.status, 
                        data[CONF_URL]
                    )
    except Exception as err:
        _LOGGER.error("Failed to connect to %s: %s", data[CONF_URL], err)
        raise

    return {
        CONF_NAME: data[CONF_NAME],
        CONF_URL: data[CONF_URL],
        CONF_METHOD: data[CONF_METHOD],
        CONF_TIMEOUT: data[CONF_TIMEOUT],
        CONF_UPDATE_INTERVAL: data[CONF_UPDATE_INTERVAL],
        CONF_VERIFY_SSL: data[CONF_VERIFY_SSL],
        CONF_EXPECTED_STATUS: expected_status,
        CONF_HEADERS: headers,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HTTP Uptime Monitor."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=info[CONF_NAME], data=info)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
