"""
Virtual Climate ECU.

Provides:
1. GetCabinTemperature method
2. SetTargetTemperature method
3. CabinTemperatureChanged event
"""

import asyncio
import logging
from typing import Tuple

from someipy import (
    MessageType,
    Method,
    MethodResult,
    ReturnCode,
    ServerServiceInstance,
    ServiceBuilder,
    TransportLayerProtocol,
    connect_to_someipy_daemon,
)

from someipy.someipy_logging import set_someipy_log_level
from someipy.serialization import Sint16

from climate_interface import (
    SERVICE_ID,
    INSTANCE_ID,
    MAJOR_VERSION,
    INTERFACE_IP,
    PROVIDER_PORT,
    GET_CABIN_TEMPERATURE_METHOD_ID,
    SET_TARGET_TEMPERATURE_METHOD_ID,
    CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    CLIMATE_EVENTGROUP_ID,
    CabinTemperaturePayload,
    TemperatureStatusPayload,
    climate_eventgroup,
)


# Initial temperatures in tenths of a degree Celsius
current_cabin_temperature = 240
target_temperature = 220


async def get_cabin_temperature_handler(
    input_data: bytes,
    client_address: Tuple[str, int],
) -> MethodResult:

    print()
    print("GetCabinTemperature request received")
    print(f"Consumer address       : {client_address[0]}:{client_address[1]}")
    print(
        f"Current cabin temperature: "
        f"{current_cabin_temperature / 10:.1f} °C"
    )

    response_payload = CabinTemperaturePayload(
        current_cabin_temperature
    ).serialize()

    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response_payload

    print(f"Response bytes         : {response_payload.hex(' ')}")
    print("GetCabinTemperature response sent")

    return result


async def set_target_temperature_handler(
    input_data: bytes,
    client_address: Tuple[str, int],
) -> MethodResult:

    global target_temperature

    print()
    print("SetTargetTemperature request received")
    print(f"Consumer address       : {client_address[0]}:{client_address[1]}")

    # Decode the received signed 16-bit temperature
    requested_temperature = Sint16().deserialize(input_data).value

    print(
        f"Requested temperature : "
        f"{requested_temperature / 10:.1f} °C"
    )

    # Accept temperatures between 16.0 °C and 30.0 °C
    if 160 <= requested_temperature <= 300:

        target_temperature = requested_temperature
        status = 0

        print("Status                 : ACCEPTED")
        print(
            f"New target temperature: "
            f"{target_temperature / 10:.1f} °C"
        )

    else:

        status = 1

        print("Status                 : INVALID_TEMPERATURE")
        print(
            f"Target remains         : "
            f"{target_temperature / 10:.1f} °C"
        )

    response_payload = TemperatureStatusPayload(status).serialize()

    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response_payload

    print(f"Response bytes         : {response_payload.hex(' ')}")
    print("SetTargetTemperature response sent")

    return result


def build_provider_service():

    get_temperature_method = Method(
        id=GET_CABIN_TEMPERATURE_METHOD_ID,
        protocol=TransportLayerProtocol.UDP,
        method_handler=get_cabin_temperature_handler,
    )

    set_temperature_method = Method(
        id=SET_TARGET_TEMPERATURE_METHOD_ID,
        protocol=TransportLayerProtocol.UDP,
        method_handler=set_target_temperature_handler,
    )

    return (
        ServiceBuilder()
        .with_service_id(SERVICE_ID)
        .with_major_version(MAJOR_VERSION)
        .with_method(get_temperature_method)
        .with_method(set_temperature_method)
        .with_eventgroup(climate_eventgroup)
        .build()
    )


async def simulate_cabin_temperature(
    service_instance: ServerServiceInstance,
) -> None:

    global current_cabin_temperature

    temperature_sequence = [240, 245, 250, 255, 260]
    index = 0

    while True:

        current_cabin_temperature = temperature_sequence[index]

        print()
        print(
            f"Simulated cabin temperature changed to "
            f"{current_cabin_temperature / 10:.1f} °C"
        )

        event_payload = CabinTemperaturePayload(
            current_cabin_temperature
        ).serialize()

        service_instance.send_event(
            CLIMATE_EVENTGROUP_ID,
            CABIN_TEMPERATURE_CHANGED_EVENT_ID,
            event_payload,
        )

        print("CabinTemperatureChanged event sent")

        index = (index + 1) % len(temperature_sequence)

        await asyncio.sleep(2)


async def main() -> None:

    set_someipy_log_level(logging.INFO)

    print("=" * 60)
    print("Virtual Climate ECU")
    print("ClimateService Provider")
    print("=" * 60)

    print(f"Service ID       : 0x{SERVICE_ID:04X}")
    print(f"Instance ID      : 0x{INSTANCE_ID:04X}")
    print(f"Provider endpoint: {INTERFACE_IP}:{PROVIDER_PORT}")
    print(f"Initial cabin temperature: {current_cabin_temperature / 10:.1f} °C")
    print(f"Initial target temperature: {target_temperature / 10:.1f} °C")

    print("=" * 60)

    print("Connecting to someipy daemon...")

    daemon = await connect_to_someipy_daemon()

    print("Connected to someipy daemon")

    provider_service = build_provider_service()

    provider_instance = ServerServiceInstance(
        daemon=daemon,
        service=provider_service,
        instance_id=INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=PROVIDER_PORT,
        ttl=5,
        cyclic_offer_delay_ms=2000,
    )

    print("Offering ClimateService...")

    await provider_instance.start_offer()

    print("ClimateService is being offered")

    temperature_task = asyncio.create_task(
        simulate_cabin_temperature(provider_instance)
    )

    try:

        await asyncio.Future()

    finally:

        temperature_task.cancel()

        try:
            await temperature_task
        except asyncio.CancelledError:
            pass

        await provider_instance.stop_offer()

        await daemon.disconnect_from_daemon()


if __name__ == "__main__":
    asyncio.run(main())
