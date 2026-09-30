# Troubleshooting

## Unable to connect to the GenieACS NBI

The setup form shows this when Home Assistant cannot reach the URL, or the NBI answers with an error other
than 401.

- The form starts with `http://localhost:7557`. On Home Assistant OS and in Docker, `localhost` is Home
  Assistant's own container. Use the host name or IP address of the machine that runs GenieACS.
- Use the NBI port, 7557 by default, not the GenieACS UI port (3000) or the CWMP port (7547).
- From the machine that runs Home Assistant, this must print a JSON list:

  ```bash
  curl 'http://genieacs:7557/devices/?projection=_id&limit=1'
  ```

## Invalid credentials

The NBI answered 401. Check the username and the password. The integration sends credentials only when both
fields are filled in; a username with an empty password sends none, and a protected NBI answers that with
401 too.

## This GenieACS instance is already configured

Each NBI URL can be added once. A trailing `/` is removed before the comparison, so `http://genieacs:7557/`
and `http://genieacs:7557` are the same instance.

## Entities are unavailable

- **All of them**: the last poll failed. The NBI is down, its address changed, or its credentials changed.
  The Home Assistant log says `Cannot reach GenieACS NBI`, or `Error fetching GenieACS devices` when the
  NBI rejects the credentials. The integration polls again every 60 seconds and
  the entities come back on their own once the NBI answers. If the NBI was down when Home Assistant started,
  the integration shows as retrying setup and Home Assistant retries it.
- **One device's**: GenieACS no longer lists that device, usually because it was deleted from the ACS.

## A new device does not show up

Devices are added when the integration starts. After GenieACS registers a new device, reload the
integration: **Settings > Devices & services > GenieACS**, the three-dot menu on the entry, **Reload**.
Restarting Home Assistant does the same.

## Online is off although the device works

Online is on when the device has reported to GenieACS in the last 5 minutes. A device reports on its periodic
inform interval (`ManagementServer.PeriodicInformInterval`). If that is longer than 300 seconds, Online turns
off between reports even though the device is up.

Either lower the interval to 300 seconds or less with a GenieACS
[provision](https://docs.genieacs.com/en/latest/provisions.html) or preset, or read Online as "reported in
the last 5 minutes". The [example automation](usage.md#example-automation) assumes the first.

## A sensor shows Unknown

The integration shows what GenieACS has stored. If the parameter is missing on the device's page in the
GenieACS UI, it is missing in Home Assistant too.

- **WAN IP address** reads `WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.ExternalIPAddress` only.
  It stays empty on a TR-181 device, which keeps its address under `Device.IP.Interface.`, on a PPPoE line,
  which uses `WANPPPConnection`, and on a device whose connection is not the first one. **Refresh
  parameters** does not fill it: that button asks for the `DeviceInfo` parameters only.
- **Firmware, Manufacturer, Model, Serial number, Uptime**: press **Refresh parameters** on the device. If
  the value is still missing after the device's next session, the device does not report it.

The parameter behind every sensor is on [How it works](how-it-works.md#parameters).

## Reboot or Refresh parameters does nothing

GenieACS queued the task but could not reach the device with a connection request, usually because the
device is behind NAT or its connection request URL is not reachable from the ACS. The task runs at the
device's next inform. The queued tasks are listed at
`http://genieacs:7557/tasks/?query={"device":"<device ID>"}`.

## Reporting a bug

Open an [issue](https://github.com/GeiserX/genieacs-ha/issues) with:

- the Home Assistant version and the integration version (HACS shows it, or `version` in
  `custom_components/genieacs/manifest.json`);
- the GenieACS version;
- the device's manufacturer and model, and whether it uses TR-181 (`Device.`) or TR-098
  (`InternetGatewayDevice.`);
- what you expected and what you saw;
- the log lines from `custom_components.genieacs`. For more detail, turn on debug logging and reproduce once:

  ```yaml
  logger:
    logs:
      custom_components.genieacs: debug
  ```

Remove device IDs, serial numbers, IP addresses and credentials from anything you paste. A security problem
goes through the [security policy](https://github.com/GeiserX/genieacs-ha/blob/main/SECURITY.md), never a
public issue.
