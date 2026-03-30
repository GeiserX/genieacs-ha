# GenieACS for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)
[![GitHub Stars](https://img.shields.io/github/stars/GeiserX/genieacs-ha.svg)](https://github.com/GeiserX/genieacs-ha/stargazers)
[![License: GPL-3.0](https://img.shields.io/github/license/GeiserX/genieacs-ha.svg)](LICENSE)

A Home Assistant custom integration for managing TR-069 CPE devices (routers, ONTs, gateways) through a [GenieACS](https://genieacs.com/) instance.

GenieACS is an open-source Auto Configuration Server (ACS) that speaks the TR-069 protocol. This integration connects to the GenieACS Northbound Interface (NBI) REST API to bring your managed network devices into Home Assistant.

## Prerequisites

- A running GenieACS instance with the NBI accessible (default port `7557`)
- One or more CPE devices connected to GenieACS via TR-069
- Home Assistant 2024.1 or later
- [HACS](https://hacs.xyz/) installed

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three-dot menu in the top right and select **Custom repositories**
3. Add `https://github.com/GeiserX/genieacs-ha` with category **Integration**
4. Search for "GenieACS" and install it
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/genieacs` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **GenieACS**
3. Enter your NBI URL (e.g., `http://genieacs:7557`)
4. Optionally enter HTTP Basic auth credentials if your NBI requires authentication
5. The integration will test the connection and discover all managed devices

## Entities

For each CPE device managed by GenieACS, the integration creates the following entities:

| Entity | Type | Description |
|--------|------|-------------|
| Online | Binary Sensor | `on` if the device reported to GenieACS within the last 5 minutes |
| WAN IP address | Sensor | External IP address from the WAN interface |
| Uptime | Sensor | Device uptime in seconds |
| Firmware | Sensor | Software version (diagnostic) |
| Manufacturer | Sensor | Device manufacturer (diagnostic) |
| Model | Sensor | Device model name (diagnostic) |
| Serial number | Sensor | Device serial number (diagnostic) |
| Reboot | Button | Send a reboot command to the device via TR-069 |
| Refresh parameters | Button | Trigger a parameter refresh from the device (diagnostic) |

## TR-181 and TR-098 Compatibility

TR-069 devices use one of two parameter tree roots:

- **TR-181**: `Device.` (newer standard)
- **TR-098**: `InternetGatewayDevice.` (older standard)

This integration automatically handles both. It checks both root paths when reading device parameters, so it works with any compliant CPE regardless of which data model it implements.

## Related Projects

- [genieacs-docker](https://github.com/GeiserX/genieacs-docker) -- Production-ready Docker deployment for GenieACS
- [genieacs-mcp](https://github.com/GeiserX/genieacs-mcp) -- Model Context Protocol server for GenieACS

## License

[GPL-3.0](LICENSE)
