"""
Common definition of the Climate SOME/IP service.
"""

from dataclasses import dataclass

from someipy import (
    Event,
    EventGroup,
    Method,
    ServiceBuilder,
    TransportLayerProtocol,
)

from someipy.serialization import SomeIpPayload, Sint16, Uint8


# Service identification
SERVICE_ID = 0x2234
INSTANCE_ID = 0x0001
MAJOR_VERSION = 1


# Method IDs
GET_CABIN_TEMPERATURE_METHOD_ID = 0x0001
SET_TARGET_TEMPERATURE_METHOD_ID = 0x0002


# Event and Event Group IDs
CABIN_TEMPERATURE_CHANGED_EVENT_ID = 0x8001
CLIMATE_EVENTGROUP_ID = 0x0001


# Network configuration
INTERFACE_IP = "127.0.0.1"
PROVIDER_PORT = 3004
CONSUMER_PORT = 3006


# Payload for cabin temperature (response and event)
@dataclass
class CabinTemperaturePayload(SomeIpPayload):
    temperature_tenths_c: Sint16

    def __init__(self, temperature: int = 240):
        self.temperature_tenths_c = Sint16(temperature)


# Payload for target temperature (method request)
@dataclass
class TargetTemperaturePayload(SomeIpPayload):
    target_temperature_tenths_c: Sint16

    def __init__(self, temperature: int = 220):
        self.target_temperature_tenths_c = Sint16(temperature)


# Payload for SetTargetTemperature response
@dataclass
class TemperatureStatusPayload(SomeIpPayload):
    status: Uint8

    def __init__(self, status: int = 0):
        self.status = Uint8(status)


# Method definitions
get_cabin_temperature_method = Method(
    id=GET_CABIN_TEMPERATURE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)

set_target_temperature_method = Method(
    id=SET_TARGET_TEMPERATURE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)


# Event definition
cabin_temperature_changed_event = Event(
    id=CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    protocol=TransportLayerProtocol.UDP,
)


# Event Group definition
climate_eventgroup = EventGroup(
    id=CLIMATE_EVENTGROUP_ID,
    events=[cabin_temperature_changed_event],
)


# Complete Climate Service definition
climate_service = (
    ServiceBuilder()
    .with_service_id(SERVICE_ID)
    .with_major_version(MAJOR_VERSION)
    .with_method(get_cabin_temperature_method)
    .with_method(set_target_temperature_method)
    .with_eventgroup(climate_eventgroup)
    .build()
)
