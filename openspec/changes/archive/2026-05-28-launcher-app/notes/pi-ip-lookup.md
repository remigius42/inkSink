<!-- spellchecker:ignore dgram gethostbyname getsockname -->

# Device IP Address Lookup (Status Screen)

The status screen shows the device's IP address for SSH access. Two approaches:

## Option A: `socket` (preferred)

```python
import socket

def get_ip() -> str:
    try:
        # Connect to an external address to determine the outbound interface IP.
        # No data is actually sent.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "unavailable"
```

Returns the IP of the interface used for outbound traffic (typically `wlan0`
on the Pi). Works without root. Returns `"unavailable"` if no network
interface is up.

## Option B: `ip addr` via subprocess (fallback)

```python
import subprocess, re

def get_ip() -> str:
    try:
        out = subprocess.check_output(
            ["ip", "-4", "addr", "show", "wlan0"],
            text=True, timeout=3,
        )
        m = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", out)
        return m.group(1) if m else "unavailable"
    except (subprocess.SubprocessError, FileNotFoundError):
        return "unavailable"
```

More explicit about the interface (`wlan0`) but subprocess-dependent and
slower. Use as fallback if Option A returns loopback (`127.x.x.x`).

## Note on `gethostbyname`

`socket.gethostbyname(socket.gethostname())` often returns `127.0.1.1` on
Pi OS (Bookworm) due to the `/etc/hosts` entry — not the WiFi IP. Avoid it.
