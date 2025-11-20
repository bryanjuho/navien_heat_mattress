"""Config flow for Navien Heat Mattress integration."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_TOKEN
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pysmartthings import SmartThings

from .const import DOMAIN, CONF_DEVICE_ID

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOKEN): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Navien Heat Mattress."""

    VERSION = 1

    def __init__(self):
        """Initialize."""
        self._token = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self._token = user_input[CONF_TOKEN]
            session = async_get_clientsession(self.hass)

            # Validate token and get devices
            try:
                api = SmartThings(session=session, _token=self._token)
                devices = await api.get_devices()

                # Filter for Navien devices if possible, or just list all
                # For now, we'll list all and let user choose
                self._devices = {d.device_id: f"{d.label} ({d.name})" for d in devices}

                if not self._devices:
                    errors["base"] = "no_devices_found"
                else:
                    return await self.async_step_device()
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the device selection step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            device_name = self._devices[device_id]

            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=device_name,
                data={
                    CONF_TOKEN: self._token,
                    CONF_DEVICE_ID: device_id,
                },
            )

        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema(
                {vol.Required(CONF_DEVICE_ID): vol.In(self._devices)}
            ),
            errors=errors,
        )
