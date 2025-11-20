import logging
from pysmartthings import SmartThings

_LOGGER = logging.getLogger(__name__)


class SmartThingsNavienClient:
    def __init__(self, session, token: str, device_id: str):
        self._st = SmartThings(session=session, _token=token)
        self._device_id = device_id

    async def get_status(self):
        try:
            return await self._st.get_device_status(self._device_id)
        except Exception as e:
            _LOGGER.error("Error getting status: %s", e)
            raise

    async def send_command(self, component, capability, command, arguments=None):
        try:
            await self._st.execute_device_command(
                self._device_id,
                capability,
                command,
                component=component,
                argument=arguments,
            )
        except Exception as e:
            _LOGGER.error("Error sending command: %s", e)
            raise
