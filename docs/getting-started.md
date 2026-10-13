# Getting started

## Prerequisites

- A running GenieACS instance whose NBI Home Assistant can reach (default port `7557`)
- One or more CPE devices connected to GenieACS via TR-069
- [HACS](https://hacs.xyz/) installed, for the HACS path

## Install with HACS

GenieACS is in the HACS default store, so there is no custom repository to add.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=GeiserX&repository=genieacs-ha&category=integration)

1. Open HACS in Home Assistant.
2. Search for **GenieACS** and open it.
3. Click **Download**.
4. Restart Home Assistant.

## Install manually

1. Copy the `custom_components/genieacs` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Configure

1. Go to **Settings > Devices & services > Add integration**.
2. Search for **GenieACS**.
3. Enter your NBI URL, for example `http://genieacs:7557`.
4. If your NBI requires authentication, enter the HTTP Basic auth username and password. Basic auth sends
   them readable to anyone on the network path, so use an `https://` NBI URL, for example through a
   reverse proxy, whenever you set credentials.
5. The integration tests the connection and discovers all managed devices.

If the URL is wrong or the NBI is down, the form says "Unable to connect to the GenieACS NBI"; wrong
credentials give "Invalid credentials". Each NBI URL can be added once.

## What working looks like

Under **Settings > Devices & services > GenieACS** there is one device per CPE, named
`<manufacturer> <model>`, or its serial number when the CPE does not report both, with nine entities:
the Online binary sensor, six sensors and two buttons. [Usage](usage.md) lists them. Values refresh
every 60 seconds.
