<p align="center">
  <img src="https://raw.githubusercontent.com/GeiserX/genieacs-ha/main/docs/images/banner.svg" alt="GenieACS for Home Assistant" width="900"/>
</p>

# GenieACS for Home Assistant

[![Tests](https://github.com/GeiserX/genieacs-ha/actions/workflows/tests.yml/badge.svg)](https://github.com/GeiserX/genieacs-ha/actions/workflows/tests.yml)
[![License: GPL-3.0](https://img.shields.io/github/license/GeiserX/genieacs-ha.svg)](https://github.com/GeiserX/genieacs-ha/blob/main/LICENSE)
[![codecov](https://codecov.io/gh/GeiserX/genieacs-ha/graph/badge.svg)](https://codecov.io/gh/GeiserX/genieacs-ha)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Stars](https://img.shields.io/github/stars/GeiserX/genieacs-ha.svg)](https://github.com/GeiserX/genieacs-ha/stargazers)

A Home Assistant custom integration for managing TR-069 CPE devices (routers, ONTs, gateways) through a [GenieACS](https://genieacs.com/) instance. It reads the GenieACS Northbound Interface (NBI) REST API and brings every managed device into Home Assistant.

## Features

- Discovers every CPE your GenieACS manages through the NBI REST API and creates one Home Assistant device per CPE.
- Online binary sensor: on when the device reported within the last 5 minutes.
- Sensors for WAN IP, uptime, firmware, manufacturer, model and serial number.
- Reboot and Refresh parameters buttons that send TR-069 tasks.
- Reads both TR-181 (`Device.`) and TR-098 (`InternetGatewayDevice.`) parameter trees.
- Optional HTTP Basic auth for the NBI; polls every 60 seconds.

## Quick start

1. In HACS, open the three-dot menu > **Custom repositories** and add `https://github.com/GeiserX/genieacs-ha` with category **Integration**.
2. Search for "GenieACS", install it, and restart Home Assistant.
3. Go to **Settings > Devices & services > Add integration** and search for **GenieACS**.
4. Enter your NBI URL, for example `http://genieacs:7557`, and the Basic auth credentials if your NBI needs them.

Manual install and what a working setup looks like are in [Getting started](https://github.com/GeiserX/genieacs-ha/blob/main/docs/getting-started.md).

## Documentation

- [Getting started](https://github.com/GeiserX/genieacs-ha/blob/main/docs/getting-started.md): prerequisites, HACS and manual install, configuration, first run
- [Usage](https://github.com/GeiserX/genieacs-ha/blob/main/docs/usage.md): the entities, TR-181 and TR-098, an example automation

## Related projects

GenieACS family: [genieacs-container](https://github.com/GeiserX/genieacs-container), [genieacs-ansible](https://github.com/GeiserX/genieacs-ansible), [genieacs-mcp](https://github.com/GeiserX/genieacs-mcp), [genieacs-services](https://github.com/GeiserX/genieacs-services), [genieacs-sim-container](https://github.com/GeiserX/genieacs-sim-container); the full list is in [genieacs-container's related projects](https://github.com/GeiserX/genieacs-container/blob/main/docs/related.md). Other Home Assistant integrations: [cashpilot-ha](https://github.com/GeiserX/cashpilot-ha), [duplicacy-ha](https://github.com/GeiserX/duplicacy-ha), [pumperly-ha](https://github.com/GeiserX/pumperly-ha).

## License

[GPL-3.0-or-later](https://github.com/GeiserX/genieacs-ha/blob/main/LICENSE)
