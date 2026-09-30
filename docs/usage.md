# Usage

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
| Refresh parameters | Button | Ask the device to report its firmware, manufacturer, model, serial number and uptime again (diagnostic) |

The buttons queue a task in GenieACS and send a connection request, so a device the ACS can reach runs
it at once; any other device runs it at its next inform.

## TR-181 and TR-098

TR-069 devices use one of two parameter tree roots:

- **TR-181**: `Device.` (newer standard)
- **TR-098**: `InternetGatewayDevice.` (older standard)

The integration reads each parameter under `Device.` first and `InternetGatewayDevice.` second, so the
device information sensors work with either model. The WAN IP address sensor reads a TR-098 path only and
stays empty on TR-181 devices and PPPoE lines; [How it works](how-it-works.md#parameters) lists every path.

## Example automation

Notify when a router stops reporting to GenieACS for 10 minutes: the Online sensor turns off after 5
minutes without a report, and the trigger waits 5 more. Replace the entity ID with the one Home Assistant
gave your device's Online sensor:

```yaml
automation:
  - alias: "Router offline"
    triggers:
      - trigger: state
        entity_id: binary_sensor.acme_router_x1_online
        to: "off"
        for: "00:05:00"
    actions:
      - action: notify.notify
        data:
          message: "The router has not reported to GenieACS for 10 minutes."
```
