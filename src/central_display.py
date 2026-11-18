"""
Central Display ECU.

Consumes:
1. VehicleSpeedService
2. ClimateService
"""

import asyncio
import logging

from someipy import (
    ClientServiceInstance,
    MessageType,
    ReturnCode,
    connect_to_someipy_daemon,
)

from someipy.someipy_logging import set_someipy_log_level


# Vehicle service imports
from vehicle_speed_interface import (
    SERVICE_ID as VEHICLE_SERVICE_ID,
    INSTANCE_ID as VEHICLE_INSTANCE_ID,
    INTERFACE_IP,
    GET_SPEED_METHOD_ID,
    GET_VEHICLE_STATE_METHOD_ID,
    SPEED_CHANGED_EVENT_ID,
    OVERSPEED_WARNING_EVENT_ID,
    SpeedPayload,
    VehicleStatePayload,
    speed_eventgroup,
    overspeed_eventgroup,
    vehicle_speed_service,
)


# Climate service imports
from climate_interface import (
    SERVICE_ID as CLIMATE_SERVICE_ID,
    INSTANCE_ID as CLIMATE_INSTANCE_ID,
    GET_CABIN_TEMPERATURE_METHOD_ID,
    SET_TARGET_TEMPERATURE_METHOD_ID,
    CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    CabinTemperaturePayload,
    TargetTemperaturePayload,
    TemperatureStatusPayload,
    climate_eventgroup,
    climate_service,
)


# Separate consumer ports
VEHICLE_CONSUMER_PORT = 3008
CLIMATE_CONSUMER_PORT = 3006


# --------------------------------------------------
# VEHICLE EVENT CALLBACK
# --------------------------------------------------

def vehicle_event_callback(
    event_id: int,
    event_payload: bytes,
) -> None:

    try:

        speed_message = SpeedPayload().deserialize(
            event_payload
        )

        speed = speed_message.speed_kmph.value

        if event_id == SPEED_CHANGED_EVENT_ID:

            print()
            print("Vehicle Speed Updated")
            print(f"Vehicle Speed : {speed} km/h")

        elif event_id == OVERSPEED_WARNING_EVENT_ID:

            print()
            print("=" * 45)
            print("OVERSPEED WARNING")
            print(f"Vehicle Speed : {speed} km/h")
            print("=" * 45)

    except Exception as error:

        print(f"Vehicle event decoding failed: {error}")


# --------------------------------------------------
# CLIMATE EVENT CALLBACK
# --------------------------------------------------

def climate_event_callback(
    event_id: int,
    event_payload: bytes,
) -> None:

    try:

        if event_id == CABIN_TEMPERATURE_CHANGED_EVENT_ID:

            temperature_message = (
                CabinTemperaturePayload().deserialize(
                    event_payload
                )
            )

            temperature = (
                temperature_message.temperature_tenths_c.value
            )

            print()
            print(
                f"Cabin Temperature Updated : "
                f"{temperature / 10:.1f} °C"
            )

    except Exception as error:

        print(f"Climate event decoding failed: {error}")


# --------------------------------------------------
# VEHICLE METHOD CALLS
# --------------------------------------------------

async def call_vehicle_methods(
    client_instance: ClientServiceInstance,
) -> None:

    # GetSpeed
    try:

        print()
        print("Calling GetSpeed...")

        result = await client_instance.call_method(
            GET_SPEED_METHOD_ID,
            b"",
        )

        if (
            result.message_type == MessageType.RESPONSE
            and result.return_code == ReturnCode.E_OK
        ):

            speed_message = SpeedPayload().deserialize(
                result.payload
            )

            print(
                f"Vehicle Speed : "
                f"{speed_message.speed_kmph.value} km/h"
            )

    except Exception as error:

        print(f"GetSpeed failed: {error}")


    # GetVehicleState
    try:

        print()
        print("Calling GetVehicleState...")

        result = await client_instance.call_method(
            GET_VEHICLE_STATE_METHOD_ID,
            b"",
        )

        if (
            result.message_type == MessageType.RESPONSE
            and result.return_code == ReturnCode.E_OK
        ):

            state_message = VehicleStatePayload().deserialize(
                result.payload
            )

            state = state_message.state.value

            if state == 0:
                state_name = "STOPPED"
            else:
                state_name = "MOVING"

            print(f"Vehicle State : {state_name}")

    except Exception as error:

        print(f"GetVehicleState failed: {error}")


# --------------------------------------------------
# CLIMATE METHOD CALLS
# --------------------------------------------------

async def call_climate_methods(
    client_instance: ClientServiceInstance,
) -> None:

    # GetCabinTemperature
    try:

        print()
        print("Calling GetCabinTemperature...")

        result = await client_instance.call_method(
            GET_CABIN_TEMPERATURE_METHOD_ID,
            b"",
        )

        if (
            result.message_type == MessageType.RESPONSE
            and result.return_code == ReturnCode.E_OK
        ):

            temperature_message = (
                CabinTemperaturePayload().deserialize(
                    result.payload
                )
            )

            temperature = (
                temperature_message.temperature_tenths_c.value
            )

            print(
                f"Cabin Temperature : "
                f"{temperature / 10:.1f} °C"
            )

    except Exception as error:

        print(f"GetCabinTemperature failed: {error}")


    # SetTargetTemperature validation tests
    test_temperatures = [220, 160, 300, 100, 350]

    for requested_temperature in test_temperatures:
        try:
            request_payload = TargetTemperaturePayload(
                requested_temperature
            ).serialize()

            print()
            print("=" * 45)
            print(
                f"Testing Target Temperature: "
                f"{requested_temperature / 10:.1f} °C"
            )

            result = await client_instance.call_method(
                SET_TARGET_TEMPERATURE_METHOD_ID,
                request_payload
            )

            if (
                result.message_type == MessageType.RESPONSE
                and result.return_code == ReturnCode.E_OK
            ):
                status_message = TemperatureStatusPayload().deserialize(
                    result.payload
                )

                status = status_message.status.value

                if status == 0:
                    print("Result: ACCEPTED")
                else:
                    print("Result: INVALID_TEMPERATURE")
            else:
                print("No valid response received")

        except Exception as error:
            print(f"SetTargetTemperature failed: {error}")

        await asyncio.sleep(1)

# --------------------------------------------------
# VEHICLE SERVICE MONITOR
# --------------------------------------------------

async def monitor_vehicle_service(
    client_instance: ClientServiceInstance,
) -> None:

    while True:

        if await client_instance.is_available():

            print()
            print("VehicleSpeedService : AVAILABLE")

            print("Subscribing to SpeedChanged...")

            client_instance.subscribe_eventgroup(
                speed_eventgroup,
                5,
            )

            print("Subscribing to OverspeedWarning...")

            client_instance.subscribe_eventgroup(
                overspeed_eventgroup,
                5,
            )

            await call_vehicle_methods(client_instance)

            while await client_instance.is_available():
                await asyncio.sleep(1)

            print()
            print("VehicleSpeedService : NOT AVAILABLE")

        else:

            print("VehicleSpeedService : NOT AVAILABLE")
            await asyncio.sleep(2)


# --------------------------------------------------
# CLIMATE SERVICE MONITOR
# --------------------------------------------------

async def monitor_climate_service(
    client_instance: ClientServiceInstance,
) -> None:

    while True:

        if await client_instance.is_available():

            print()
            print("ClimateService : AVAILABLE")

            print("Subscribing to CabinTemperatureChanged...")

            client_instance.subscribe_eventgroup(
                climate_eventgroup,
                5,
            )

            await call_climate_methods(client_instance)

            while await client_instance.is_available():
                await asyncio.sleep(1)

            print()
            print("ClimateService : NOT AVAILABLE")

        else:

            print("ClimateService : NOT AVAILABLE")
            await asyncio.sleep(2)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

async def main() -> None:

    set_someipy_log_level(logging.INFO)

    print("=" * 60)
    print("CENTRAL VEHICLE DISPLAY")
    print("=" * 60)

    print(
        f"VehicleSpeedService ID : "
        f"0x{VEHICLE_SERVICE_ID:04X}"
    )

    print(
        f"ClimateService ID      : "
        f"0x{CLIMATE_SERVICE_ID:04X}"
    )

    print("=" * 60)

    print("Connecting to someipy daemon...")

    daemon = await connect_to_someipy_daemon()

    print("Connected to someipy daemon")

    # Vehicle service client
    vehicle_client = ClientServiceInstance(
        daemon=daemon,
        service=vehicle_speed_service,
        instance_id=VEHICLE_INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=VEHICLE_CONSUMER_PORT,
    )

    vehicle_client.register_callback(
        vehicle_event_callback
    )

    # Climate service client
    climate_client = ClientServiceInstance(
        daemon=daemon,
        service=climate_service,
        instance_id=CLIMATE_INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=CLIMATE_CONSUMER_PORT,
    )

    climate_client.register_callback(
        climate_event_callback
    )

    print()
    print("Searching for services...")

    print("VehicleSpeedService : NOT AVAILABLE")
    print("ClimateService      : NOT AVAILABLE")

    vehicle_task = asyncio.create_task(
        monitor_vehicle_service(vehicle_client)
    )

    climate_task = asyncio.create_task(
        monitor_climate_service(climate_client)
    )

    try:

        await asyncio.Future()

    finally:

        vehicle_task.cancel()
        climate_task.cancel()

        try:
            await vehicle_task
        except asyncio.CancelledError:
            pass

        try:
            await climate_task
        except asyncio.CancelledError:
            pass

        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nCentral Display stopped")
