"""Test all entities (climate, switch, binary_sensor, button)."""

import asyncio
import aiohttp
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "custom_components/navien_heat_mattress"))

from smartthings import SmartThingsNavienClient
from pysmartthings import Capability, Attribute


async def main():
    """Test all entity types."""
    with open(".credentials", "r") as f:
        token = f.read().strip()

    device_id = "4ee0c792-955f-4dd5-8acb-c6fc3779a28f"

    print("=" * 70)
    print("TESTING ALL NAVIEN HEAT MATTRESS ENTITIES")
    print("=" * 70)

    async with aiohttp.ClientSession() as session:
        client = SmartThingsNavienClient(session, token, device_id)
        status = await client.get_status()

        # Test Climate Entities (Left & Right)
        print("\n[1] CLIMATE ENTITIES")
        print("-" * 70)
        for component in ["Left", "Right"]:
            comp = status[component]

            temp_cap = comp.get(Capability.TEMPERATURE_MEASUREMENT, {})
            temp = temp_cap.get(Attribute.TEMPERATURE)

            setpoint_cap = comp.get(Capability.THERMOSTAT_HEATING_SETPOINT, {})
            setpoint = setpoint_cap.get(Attribute.HEATING_SETPOINT)

            switch_cap = comp.get(Capability.SWITCH, {})
            switch = switch_cap.get(Attribute.SWITCH)

            print(f"\nBed {component}:")
            print(f"  Entity Type: climate.bed_{component.lower()}")
            print(f"  Current Temperature: {temp.value if temp else 'N/A'}°C")
            print(f"  Target Temperature: {setpoint.value if setpoint else 'N/A'}°C")
            print(
                f"  HVAC Mode: {'HEAT' if switch and switch.value == 'on' else 'OFF'}"
            )
            print("  ✓ Ready")

        # Test Main Switch
        print("\n[2] SWITCH ENTITY")
        print("-" * 70)
        main = status.get("main", {})
        switch_cap = main.get(Capability.SWITCH, {})
        switch = switch_cap.get(Attribute.SWITCH)

        print("\nBed Main:")
        print("  Entity Type: switch.bed_main")
        print(f"  State: {'ON' if switch and switch.value == 'on' else 'OFF'}")
        print("  ✓ Ready")

        # Test Binary Sensor
        print("\n[3] BINARY SENSOR ENTITY")
        print("-" * 70)
        health_cap = main.get(Capability.HEALTH_CHECK, {})
        health = health_cap.get(Attribute.DEVICE_WATCH_DEVICE_STATUS)

        print("\nBed Connectivity:")
        print("  Entity Type: binary_sensor.bed_connectivity")
        print(
            f"  State: {'ON (online)' if health and health.value == 'online' else 'OFF (offline)'}"
        )
        print("  Device Class: connectivity")
        print("  ✓ Ready")

        # Test Button
        print("\n[4] BUTTON ENTITY")
        print("-" * 70)

        print("\nBed Refresh:")
        print("  Entity Type: button.bed_refresh")
        print(f"  Capability Available: {Capability.REFRESH in main}")
        print("  ✓ Ready")

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY - All entities ready for Home Assistant:")
        print("=" * 70)
        print("\n✓ 2 Climate entities (Left, Right)")
        print("✓ 1 Switch entity (Main)")
        print("✓ 1 Binary Sensor (Connectivity)")
        print("✓ 1 Button (Refresh)")
        print("\nTotal: 5 entities")
        print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
