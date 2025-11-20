"""Switch platform for Navien Heat Mattress."""

import logging
from homeassistant.components.switch import SwitchEntity
from pysmartthings import Capability, Command, Attribute

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Navien switch."""
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NavienMainSwitch(client)], update_before_add=True)


class NavienMainSwitch(SwitchEntity):
    """Representation of the main switch for Navien mattress."""

    def __init__(self, client):
        """Initialize the switch."""
        self._client = client
        self._attr_name = "Bed Main"
        self._attr_unique_id = f"{client._device_id}_main_switch".lower()
        self._is_on = False

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        try:
            await self._client.send_command(
                "main",
                Capability.SWITCH,
                Command.ON,
                None,
            )
            self._is_on = True
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to turn on: %s", e)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        try:
            await self._client.send_command(
                "main",
                Capability.SWITCH,
                Command.OFF,
                None,
            )
            self._is_on = False
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to turn off: %s", e)

    async def async_update(self):
        """Update the switch state."""
        try:
            status = await self._client.get_status()
            main = status.get("main", {})

            switch_cap = main.get(Capability.SWITCH, {})
            switch_attr = switch_cap.get(Attribute.SWITCH)
            if switch_attr:
                self._is_on = switch_attr.value == "on"
        except Exception as e:
            _LOGGER.error("Failed to update switch: %s", e)
