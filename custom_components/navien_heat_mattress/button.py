"""Button platform for Navien Heat Mattress."""

import logging
from homeassistant.components.button import ButtonEntity
from pysmartthings import Capability, Command

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Navien buttons."""
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NavienRefreshButton(client)])


class NavienRefreshButton(ButtonEntity):
    """Representation of a refresh button."""

    def __init__(self, client):
        """Initialize the button."""
        self._client = client
        self._attr_name = "Bed Refresh"
        self._attr_unique_id = f"{client._device_id}_refresh".lower()

    async def async_press(self):
        """Handle the button press."""
        try:
            await self._client.send_command(
                "main",
                Capability.REFRESH,
                Command.REFRESH,
                None,
            )
            _LOGGER.info("Refresh command sent successfully")
        except Exception as e:
            _LOGGER.error("Failed to send refresh command: %s", e)
