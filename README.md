# SOME/IP Multi-ECU Communication Using Python

## Project Overview

This project demonstrates Service-Oriented Communication (SoC) in an automotive network using the SOME/IP protocol.

A virtual vehicle network is implemented using Python and the `someipy` library. Four logical ECUs communicate through two SOME/IP services, demonstrating service discovery, request-response communication, event notifications, multiple consumers, and service failure recovery.

## Objectives

- Understand the SOME/IP protocol and its communication model.
- Implement service-oriented communication between multiple ECUs.
- Configure service discovery.
- Implement methods and event notifications.
- Demonstrate multiple consumers accessing the same service.
- Demonstrate one consumer accessing multiple services.
- Analyse SOME/IP communication using Wireshark.

## System Architecture

The project consists of four logical ECUs:

1. **Vehicle ECU:** Provides vehicle speed and vehicle state information.
2. **Instrument Cluster ECU:** Consumes vehicle speed and vehicle state information.
3. **Climate ECU:** Provides cabin temperature information and handles target temperature requests.
4. **Central Display ECU:** Consumes both VehicleSpeedService and ClimateService.

The SOME/IP daemon handles service discovery and communication support.

## Services Implemented

### 1. VehicleSpeedService

- Service ID: `0x1234`
- Instance ID: `0x5678`

**Methods:**
- `GetSpeed()` – Returns the current vehicle speed.
- `GetVehicleState()` – Returns whether the vehicle is stopped or moving.

**Events:**
- `SpeedChanged` – Notifies subscribers when vehicle speed changes.
- `OverspeedWarning` – Notifies subscribers when speed exceeds 80 km/h.

### 2. ClimateService

- Service ID: `0x2234`
- Instance ID: `0x0001`

**Methods:**
- `GetCabinTemperature()` – Returns the current cabin temperature.
- `SetTargetTemperature()` – Accepts or rejects a requested target temperature.

**Event:**
- `CabinTemperatureChanged` – Notifies subscribers when cabin temperature changes.

The valid target temperature range is 16°C to 30°C.

## Project Structure

```text
someip-python-assignment/
│
├── captures/
│   ├── assignment1-someip.pcapng
│   ├── assignment2-multi-ecu.pcapng
│   └── someip_event_analysis.pcapng
│
├── config/
│   └── someipyd.json
│
├── images/
│   └── Project screenshots
│
├── src/
│   ├── central_display.py
│   ├── climate_interface.py
│   ├── climate_service.py
│   ├── cluster_client.py
│   ├── vehicle_speed_interface.py
│   └── vehicle_speed_service.py
│
├── .gitignore
└── README.md
```

## How to Execute the Project

### 1. Clone the Repository

```bash
git clone https://github.com/tithi164/SomeIP-MultiECU-Communication.git
cd SomeIP-MultiECU-Communication
```

### 2. Create a Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the `someipy` library:

```bash
pip install someipy
```

### 4. Start the SOME/IP Daemon

Open a terminal and start the SOME/IP daemon using the provided configuration:

```bash
someipyd -c config/someipyd.json
```

Keep this terminal running.

### 5. Start the Consumer ECUs

Open separate terminals, activate the virtual environment in each, and run:

**Terminal 2 – Instrument Cluster ECU**

```bash
python src/cluster_client.py
```

**Terminal 3 – Central Display ECU**

```bash
python src/central_display.py
```

### 6. Start the Provider ECUs

Open two more terminals and run:

**Terminal 4 – Vehicle ECU**

```bash
python src/vehicle_speed_service.py
```

**Terminal 5 – Climate ECU**

```bash
python src/climate_service.py
```

### 7. Observe Communication

Once all components are running:

- The Vehicle ECU provides vehicle speed and vehicle state information.
- The Instrument Cluster receives vehicle information and event notifications.
- The Climate ECU provides cabin temperature and processes target temperature requests.
- The Central Display consumes both VehicleSpeedService and ClimateService.
- Service discovery allows consumers to identify available services.
- Event notifications are delivered to subscribed consumers.

Press `Ctrl + C` in each terminal to stop the corresponding process.

## Implementation and Testing

The implementation demonstrates:

- SOME/IP service discovery.
- Method request and response communication.
- Event-based publish-subscribe communication.
- Multiple consumers accessing VehicleSpeedService.
- Central Display accessing multiple services.
- Target temperature validation.
- Independent service availability and recovery.
- Wireshark traffic analysis.

## Wireshark Analysis

Wireshark was used to capture and analyse SOME/IP communication over the loopback interface.

The analysis included:

- SOME/IP Service Discovery traffic.
- VehicleSpeedService and ClimateService identifiers.
- Method requests and responses.
- Target temperature validation response.
- Event communication observed through application output.

The Wireshark capture files are available in the `captures/` directory.

## Technologies Used

- Python
- SOME/IP
- someipy
- Linux / Ubuntu
- Wireshark
- UDP
- VirtualBox

## Conclusion

This project demonstrates a multi-ECU automotive communication system using SOME/IP. It illustrates service discovery, request-response communication, event-based communication, multiple service consumers, and independent service operation.

The implementation provides practical understanding of Service-Oriented Architecture in automotive communication systems.
