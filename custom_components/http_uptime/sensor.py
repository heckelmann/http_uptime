"""Sensor platform for HTTP Uptime Monitor."""
from __future__ import annotations

import asyncio
import logging
import ssl
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_LAST_FAILURE,
    ATTR_LAST_SUCCESS,
    ATTR_RESPONSE_TIME,
    ATTR_SSL_EXPIRES,
    ATTR_STATUS_CODE,
    ATTR_URL,
    CONF_EXPECTED_STATUS,
    CONF_HEADERS,
    CONF_METHOD,
    CONF_TIMEOUT,
    CONF_UPDATE_INTERVAL,
    CONF_VERIFY_SSL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class HTTPUptimeCoordinator(DataUpdateCoordinator):
    """Class to manage fetching HTTP endpoint data."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: dict[str, Any],
    ) -> None:
        """Initialize the coordinator."""
        self.config = config
        self._session: aiohttp.ClientSession | None = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{config[CONF_NAME]}",
            update_interval=timedelta(seconds=config[CONF_UPDATE_INTERVAL]),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the HTTP endpoint."""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self.config[CONF_TIMEOUT])
            connector = aiohttp.TCPConnector(verify_ssl=self.config[CONF_VERIFY_SSL])
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.config.get(CONF_HEADERS, {}),
            )

        start_time = dt_util.utcnow()
        
        try:
            async with self._session.request(
                self.config[CONF_METHOD],
                self.config[CONF_URL],
            ) as response:
                end_time = dt_util.utcnow()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                # Check SSL certificate expiration if HTTPS
                ssl_expires = None
                if (
                    self.config[CONF_URL].startswith("https://")
                    and self.config[CONF_VERIFY_SSL]
                    and response.connection
                ):
                    try:
                        transport = response.connection.transport
                        if hasattr(transport, "get_extra_info"):
                            ssl_object = transport.get_extra_info("ssl_object")
                            if ssl_object:
                                cert = ssl_object.getpeercert()
                                if cert:
                                    ssl_expires = datetime.strptime(
                                        cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
                                    )
                    except Exception as err:
                        _LOGGER.debug("Could not get SSL info: %s", err)

                is_up = response.status in self.config[CONF_EXPECTED_STATUS]
                
                return {
                    "status_code": response.status,
                    "response_time": round(response_time, 2),
                    "is_up": is_up,
                    "last_success": dt_util.utcnow() if is_up else None,
                    "last_failure": dt_util.utcnow() if not is_up else None,
                    "ssl_expires": ssl_expires,
                    "url": self.config[CONF_URL],
                }
                
        except asyncio.TimeoutError as err:
            raise UpdateFailed(f"Timeout connecting to {self.config[CONF_URL]}") from err
        except Exception as err:
            raise UpdateFailed(f"Error connecting to {self.config[CONF_URL]}: {err}") from err

    async def async_close(self) -> None:
        """Close the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HTTP Uptime Monitor sensors."""
    coordinator = HTTPUptimeCoordinator(hass, config_entry.data)
    
    await coordinator.async_config_entry_first_refresh()
    
    async_add_entities([HTTPUptimeSensor(coordinator, config_entry)], True)


class HTTPUptimeSensor(CoordinatorEntity, SensorEntity):
    """Representation of an HTTP Uptime Monitor sensor."""

    def __init__(
        self,
        coordinator: HTTPUptimeCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = config_entry.data[CONF_NAME]
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}"
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = ["up", "down"]

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return "up" if self.coordinator.data.get("is_up") else "down"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes."""
        if self.coordinator.data is None:
            return None
            
        data = self.coordinator.data
        attributes = {
            ATTR_STATUS_CODE: data.get("status_code"),
            ATTR_RESPONSE_TIME: data.get("response_time"),
            ATTR_URL: data.get("url"),
        }
        
        if data.get("last_success"):
            attributes[ATTR_LAST_SUCCESS] = data["last_success"].isoformat()
        if data.get("last_failure"):
            attributes[ATTR_LAST_FAILURE] = data["last_failure"].isoformat()
        if data.get("ssl_expires"):
            attributes[ATTR_SSL_EXPIRES] = data["ssl_expires"].isoformat()
            
        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        if self.coordinator.data is None:
            return "mdi:help-circle"
        return "mdi:check-circle" if self.coordinator.data.get("is_up") else "mdi:close-circle"

    async def async_will_remove_from_hass(self) -> None:
        """Clean up when entity is removed."""
        await self.coordinator.async_close()
