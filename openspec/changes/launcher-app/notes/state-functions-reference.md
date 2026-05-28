# State Functions Reference

All functions live in `src/inksink/core/state.py`. Each follows the existing
pattern: safe to call on a dev machine, returns a sentinel value (never raises)
when hardware or system tools are unavailable.

## Existing functions

```python
def battery_percent() -> int:
    """0–100 from PiSugar I2C; -1 if unavailable."""

def wifi_status() -> WifiStatus:
    """nmcli-based WiFi read; sentinel WifiStatus(connected=False, ...) on error."""

@dataclass(frozen=True)
class WifiStatus:
    connected: bool
    ssid: str | None
    strength: int        # 0–100 signal quality; -1 if unavailable
```

## New functions (to be added)

```python
def ip_address() -> str:
    """Outbound-interface IP via socket connect trick (see notes/pi-ip-lookup.md).
    Fallback "unavailable" on OSError or loopback result."""

def hostname() -> str:
    """socket.gethostname(); fallback "unknown"."""

def version_info() -> str:
    """os.environ.get("INKSINK_VERSION", "unknown").
    Set by Ansible at deploy time via:
      Environment=INKSINK_VERSION={{ lookup('pipe', 'git describe --tags') }}
    Dependency: ansible-roles change must inject this env var into the
    systemd service unit.
    """

def load_averages() -> tuple[float, float, float]:
    """os.getloadavg() → (1m, 5m, 15m); (-1.0, -1.0, -1.0) on OSError."""

def memory_info() -> MemoryInfo:
    """Parse /proc/meminfo for MemTotal and MemAvailable.
    MemAvailable is used for free (not MemFree) — it accounts for reclaimable
    cache and gives a more accurate picture of actually usable memory.
    Sentinel: MemoryInfo(total_mb=-1, free_mb=-1) on any read error.
    """

def storage_info() -> StorageInfo:
    """shutil.disk_usage("/") → total/free in GB.
    Sentinel: StorageInfo(total_gb=-1.0, free_gb=-1.0) on OSError.
    """

def bluetooth_status() -> BluetoothStatus:
    """Two subprocess calls (2s timeout each):
      bluetoothctl show         → detect if adapter is powered on
      bluetoothctl devices Connected → list connected devices
    Device label: friendly Name field; fallback to MAC address.
    Sentinel: BluetoothStatus(enabled=False, connected_devices=[]) on error.
    """

@dataclass(frozen=True)
class MemoryInfo:
    total_mb: int
    free_mb: int

@dataclass(frozen=True)
class StorageInfo:
    total_gb: float
    free_gb: float

@dataclass(frozen=True)
class BluetoothStatus:
    enabled: bool
    connected_devices: list[str]  # friendly name or MAC; empty if none
```

## Display format for sentinel values

Render `-1` / `-1.0` / empty as `"unavailable"` in the STATUS screen HTML.
