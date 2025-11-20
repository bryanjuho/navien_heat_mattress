import logging
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.const import UnitOfTemperature

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

COMPONENTS = ["Left", "Right"]

async def async_setup_entry(hass, entry, async_add_entities):
    client = hass.data[DOMAIN][entry.entry_id]
    entities = [NavienBedClimate(client, comp) for comp in COMPONENTS]
    async_add_entities(entities, update_before_add=True)


class NavienBedClimate(ClimateEntity):
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(self, client, component: str):
        self._client = client
        self._component = component
        self._attr_name = f"Bed {component}"
        # Ensure unique_id is unique per device and component
        self._attr_unique_id = f"{client._device_id}_{component}".lower()
        self._current_temp = None
        self._target_temp = None
        self._hvac_mode = HVACMode.OFF

    @property
    def current_temperature(self):
        return self._current_temp

    @property
    def target_temperature(self):
        return self._target_temp

    @property
    def hvac_mode(self):
        return self._hvac_mode

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        try:
            await self._client.send_command(
                self._component,
                "thermostatHeatingSetpoint",
                "setHeatingSetpoint",
                [float(temperature)],
            )
            self._target_temp = temperature
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to set temperature: %s", e)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode):
        if hvac_mode == HVACMode.OFF:
            cmd = "off"
        else:
            cmd = "on"
        try:
            await self._client.send_command(
                self._component,
                "switch",
                cmd,
                [],
            )
            self._hvac_mode = hvac_mode
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to set hvac mode: %s", e)

    async def async_update(self):
        try:
            status = await self._client.get_status()
            comp = status["components"][self._component]

            self._current_temp = comp["temperatureMeasurement"]["temperature"]["value"]
            self._target_temp = comp["thermostatHeatingSetpoint"]["heatingSetpoint"]["value"]

            switch_state = comp["switch"]["switch"]["value"]
            self._hvac_mode = HVACMode.HEAT if switch_state == "on" else HVACMode.OFF
        except Exception as e:
            _LOGGER.error("Failed to update status: %s", e)
