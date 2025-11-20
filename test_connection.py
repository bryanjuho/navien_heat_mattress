import asyncio
import aiohttp
import sys
import os

# Add the custom component directory to path so we can import from it
# This assumes the script is run from the project root
sys.path.append(os.path.join(os.getcwd(), "custom_components/navien_heat_mattress"))

# Try to import the client.
# If this fails, make sure you are in the project root and the path is correct.
try:
    from smartthings import SmartThingsNavienClient
except ImportError:
    # Fallback for direct execution if path appending didn't work as expected
    sys.path.append(
        os.path.join(os.getcwd(), "custom_components", "navien_heat_mattress")
    )
    from smartthings import SmartThingsNavienClient

from pysmartthings import SmartThings


async def main():
    # Read token
    cred_file = ".credentials"
    if not os.path.exists(cred_file):
        print(f"Error: {cred_file} file not found.")
        return

    with open(cred_file, "r") as f:
        token = f.read().strip()

    if not token:
        print(f"Error: {cred_file} file is empty.")
        return

    print(f"Using token: {token[:4]}...{token[-4:]}")

    async with aiohttp.ClientSession() as session:
        st = SmartThings(session=session, _token=token)

        print("Connecting to SmartThings API...")
        try:
            devices = await st.get_devices()
        except Exception as e:
            print(f"Error connecting/fetching devices: {e}")
            return

        if not devices:
            print("No devices found on this account.")
            return

        print(f"Found {len(devices)} devices:")
        target_device = None

        for device in devices:
            print(
                f"- Name: {device.name}, Label: {device.label}, ID: {device.device_id}"
            )
            # Simple heuristic to find the Navien device
            if "MateWmFloatDouble" in (device.name or ""):
                target_device = device

        if target_device:
            print(f"\nFound potential Navien device: {target_device.label}")
            print(
                f"Testing SmartThingsNavienClient with device ID: {target_device.device_id}"
            )

            client = SmartThingsNavienClient(session, token, target_device.device_id)
            try:
                print("Fetching device status...")
                status = await client.get_status()
                print("Successfully retrieved status!")
                # Print some interesting attributes if available
                print(f"Status: {status}")
            except Exception as e:
                print(f"Error getting status: {e}")
        else:
            print("\nNo device with 'Navien' in name found automatically.")
            print(
                "Please update the script to use one of the Device IDs listed above if you wish to test the client."
            )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
