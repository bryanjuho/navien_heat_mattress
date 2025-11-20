"""Binary sensor platform for Navien Heat Mattress."""

import logging
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from pysmartthings import Capability, Attribute

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Navien binary sensors."""
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NavienHealthSensor(client)], update_before_add=True)


class NavienHealthSensor(BinarySensorEntity):
    """Representation of device health status."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, client):
        """Initialize the sensor."""
        self._client = client
        self._attr_name = "Bed Connectivity"
        self._attr_unique_id = f"{client._device_id}_health".lower()
        self._is_on = False

    @property
    def is_on(self):
        """Return true if device is online."""
        return self._is_on

    async def async_update(self):
        """Update the sensor state."""
        try:
            status = await self._client.get_status()
            main = status.get("main", {})

            health_cap = main.get(Capability.HEALTH_CHECK, {})
            health_attr = health_cap.get(Attribute.DEVICE_WATCH_DEVICE_STATUS)
            if health_attr:
                self._is_on = health_attr.value == "online"
        except Exception as e:
            _LOGGER.error("Failed to update health sensor: %s", e)
            self._is_on = False
