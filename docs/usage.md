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
| Refresh parameters | Button | Trigger a parameter refresh from the device (diagnostic) |

The buttons queue a task in GenieACS and send a connection request, so a device the ACS can reach runs
it at once; any other device runs it at its next inform.

## TR-181 and TR-098

TR-069 devices use one of two parameter tree roots:

- **TR-181**: `Device.` (newer standard)
- **TR-098**: `InternetGatewayDevice.` (older standard)

The integration checks both root paths when reading device parameters, so it works with any compliant
CPE whichever data model it implements.

## Example automation

Notify when a router stops reporting to GenieACS for 10 minutes. Replace the entity ID with the one
Home Assistant gave your device's Online sensor:

```yaml
automation:
  - alias: "Router offline"
    triggers:
      - trigger: state
        entity_id: binary_sensor.acme_router_x1_online
        to: "off"
        for: "00:10:00"
    actions:
      - action: notify.notify
        data:
          message: "The router has not reported to GenieACS for 10 minutes."
```
