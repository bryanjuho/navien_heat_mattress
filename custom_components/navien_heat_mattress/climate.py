import logging
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature
from pysmartthings import Capability, Command, Attribute

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
        self._attr_min_temp = 28
        self._attr_max_temp = 45
        self._attr_target_temperature_step = 0.5

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
                Capability.THERMOSTAT_HEATING_SETPOINT,
                Command.SET_HEATING_SETPOINT,
                [float(temperature)],
            )
            self._target_temp = temperature
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to set temperature: %s", e)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode):
        if hvac_mode == HVACMode.OFF:
            cmd = Command.OFF
        else:
            cmd = Command.ON
        try:
            await self._client.send_command(
                self._component,
                Capability.SWITCH,
                cmd,
                None,
            )
            self._hvac_mode = hvac_mode
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to set hvac mode: %s", e)

    async def async_update(self):
        try:
            status = await self._client.get_status()
            comp = status[self._component]

            # Extract temperature measurement
            temp_cap = comp.get(Capability.TEMPERATURE_MEASUREMENT, {})
            temp_attr = temp_cap.get(Attribute.TEMPERATURE)
            if temp_attr:
                self._current_temp = temp_attr.value

            # Extract heating setpoint
            setpoint_cap = comp.get(Capability.THERMOSTAT_HEATING_SETPOINT, {})
            setpoint_attr = setpoint_cap.get(Attribute.HEATING_SETPOINT)
            if setpoint_attr:
                self._target_temp = setpoint_attr.value

            # Extract switch state
            switch_cap = comp.get(Capability.SWITCH, {})
            switch_attr = switch_cap.get(Attribute.SWITCH)
            if switch_attr:
                switch_state = switch_attr.value
                self._hvac_mode = (
                    HVACMode.HEAT if switch_state == "on" else HVACMode.OFF
                )
        except Exception as e:
            _LOGGER.error("Failed to update status: %s", e)
