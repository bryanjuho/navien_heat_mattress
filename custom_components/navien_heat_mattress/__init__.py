from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_DEVICE_ID
from .smartthings import SmartThingsNavienClient


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    session = hass.helpers.aiohttp_client.async_get_clientsession()

    client = SmartThingsNavienClient(
        session,
        token=entry.data[CONF_TOKEN],
        device_id=entry.data[CONF_DEVICE_ID],
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, ["climate"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, ["climate"]
    ):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
