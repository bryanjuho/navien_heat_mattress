import logging
from pysmartthings import SmartThings

_LOGGER = logging.getLogger(__name__)

class SmartThingsNavienClient:
    def __init__(self, session, token: str, device_id: str):
        self._st = SmartThings(session, token)
        self._device_id = device_id

    async def get_status(self):
        try:
            device = await self._st.devices.get(self._device_id)
            return await device.status()
        except Exception as e:
            _LOGGER.error("Error getting status: %s", e)
            raise

    async def send_command(self, component, capability, command, arguments=None):
        if arguments is None:
            arguments = []
        try:
            device = await self._st.devices.get(self._device_id)
            await device.send_commands(
                [
                    {
                        "component": component,
                        "capability": capability,
                        "command": command,
                        "arguments": arguments,
                    }
                ]
            )
        except Exception as e:
            _LOGGER.error("Error sending command: %s", e)
            raise
