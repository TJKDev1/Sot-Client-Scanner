<p align="center">
  <img src="img/logo.png" alt="SoT Client Scanner Logo" width="350"/>
</p>

# Sea of Thieves Telemetry Reader

> Forked and extended — real-time Sea of Thieves telemetry dashboard powered by **mitmproxy** and **PySide6**.

![Telemetry Dashboard](img/screenshot.png)

---

## How It Works

```
Sea of Thieves  ──▶  mitmproxy (mitmdump)  ──▶  game_capture.py  ──▶  Dashboard (PySide6)
     HTTPS              intercepts traffic       parses telemetry       displays in real-time
                         via system proxy          JSON from POST         via stdout pipe
                                                   requests
```

1. The application starts `mitmdump` as a subprocess with `game_capture.py` loaded as an addon
2. The system proxy is enabled so all outbound traffic passes through mitmproxy
3. `game_capture.py` intercepts POST requests to Rare's telemetry endpoints and parses the JSON payloads
4. Parsed data is emitted to stdout in tagged format (e.g. `[POSITION]`, `[SHIP_SYSTEMS]`, `[NETWORK]`)
5. The GUI reads stdout in a background thread and updates the dashboard panels in real-time

Capture logs are written to `logs/sea_of_thieves_capture.txt` (telemetry JSON) and `logs/websocket_capture.txt` (WebSocket traffic).

---

## Features

- Real-time telemetry parsing via MITM proxy interception
- Live player position tracking with island/region detection
- Ship system monitoring (wheel, sails, capstan, cannons, harpoons, rudder, masts)
- World event detection (skull clouds, ashen lords, storms, volcanoes, forts, shipwrecks & more)
- AI / enemy tracking (skeletons, phantoms, megalodon, kraken, sirens, ocean crawlers)
- Nearby ship detection (player ships, AI ships, rowboats)
- Entity tracking (NPCs, loot, deployables, storage containers)
- Network & FPS statistics (ping, jitter, packet loss, bandwidth, frame times)
- Company progression overview with season info
- Action state tracking (60+ different states)
- Movement base tracking (ground, ship, ladder, etc.)
- Player prompts & interaction logging
- Game client metadata (build ID, platform, play mode)
- WebSocket traffic capture & logging
- Auto proxy management (Windows)
- Dark-mode dashboard

---

## Project Structure

```
Sot-Client-Scanner/
│
├── main.py                          # Application entry point
├── game_capture.py                  # mitmproxy addon (loaded by mitmdump)
├── pyproject.toml                   # Project metadata & dependencies
│
├── sot_client_scanner/              # Main application package
│   ├── __init__.py
│   ├── app.py                       # QApplication setup & launch
│   │
│   ├── constants/                   # Game data & lookup tables
│   │   ├── companies.py             # Trading company definitions
│   │   ├── game_data.py             # Action states, event keys, AI keys
│   │   └── locations.py             # Island & region coordinates
│   │
│   ├── proxy/                       # Proxy capture management
│   │   ├── parser.py                # Stdout parser for mitmproxy output
│   │   └── thread.py                # Background thread for mitmdump process
│   │
│   ├── ui/                          # PySide6 user interface
│   │   ├── main_window.py           # Main dashboard window
│   │   ├── style.py                 # Dark theme stylesheet
│   │   ├── display_names.py         # Human-readable name mappings
│   │   ├── helpers.py               # UI utility functions
│   │   └── panels/                  # Individual dashboard panels
│   │       ├── ai.py                # AI entity panel
│   │       ├── entities.py          # General entity panel
│   │       ├── network.py           # Network & FPS panel
│   │       ├── position.py          # Player position panel
│   │       ├── session.py           # Session info panel
│   │       ├── ship.py              # Ship systems panel
│   │       ├── ships.py             # Nearby ships panel
│   │       ├── status.py            # Player status panel
│   │       └── world_events.py      # World events panel
│   │
│   └── utils/                       # Shared utilities
│       ├── app.py                   # App-level helpers
│       └── proxy_control.py         # Windows proxy enable/disable
│
├── logs/                            # Auto-generated capture logs
│   ├── sea_of_thieves_capture.txt
│   └── websocket_capture.txt
│
└── img/
    └── screenshot.png
```

---

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended package manager)

| Dependency | Minimum Version |
|------------|-----------------|
| mitmproxy  | 12.2.1          |
| PySide6    | 6.10.2          |

---

## Running From Source

**With uv (recommended):**

```bash
uv sync
uv run main.py
```

**With pip:**

```bash
pip install mitmproxy PySide6
python main.py
```

1. Launch the application
2. Click **Start Capture**
3. Launch Sea of Thieves
4. The dashboard updates in real-time

---

## Building a Standalone EXE

> **Important:** Always build via `uv run pyinstaller`. Running bare `pyinstaller` uses your global Python installation and won't bundle PySide6 or mitmproxy (which live in the project venv).

```bash
uv run pyinstaller --onefile --windowed --name "SoT_Reader" main.py
```

The output EXE is placed in `dist/SoT_Reader.exe`.

**Deployment layout** — `game_capture.py` must be in the same folder as the EXE. It is loaded by `mitmdump` at runtime as an addon script and cannot be bundled inside the EXE:

```
SoT_Reader.exe
game_capture.py
```

---

## First-Time Certificate Setup

mitmproxy requires its CA certificate to be installed to intercept HTTPS traffic:

1. Run mitmproxy once:
   ```bash
   mitmproxy
   ```
2. Open in your browser:
   ```
   http://mitm.it
   ```
3. Download and install the Windows certificate
4. Close mitmproxy

Certificate location (checked automatically):

```
%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer
```

---

## Captured Telemetry

| Category | Data |
|----------|------|
| Player | Position (X/Y/Z), island/region, action state (60+), movement base, prompts, crew info |
| Ship | Type (Sloop/Brig/Galleon), active systems (wheel, sails, capstan, cannons, harpoons, rudder, masts) |
| World Events | Skull clouds, ashen lords, storms, volcanoes, forts, shipwrecks, mermaids & more |
| Nearby Ships | Player ships, AI ships (aggressive/battle/passive), rowboats |
| AI & Entities | Skeletons, phantoms, megalodon, kraken, sirens, ocean crawlers, fauna, pets |
| General Entities | NPCs, loot, consumables, deployables, mechanisms, storage containers |
| Network | Ping (RTT), jitter, packet loss, bandwidth, frame times & histogram |
| Session | Game mode, build ID, platform, window state, UI transitions, season & company progression |

For the full list of tracked keys, see [`game_capture.py`](game_capture.py).

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Proxy stuck enabled after a crash | Open **Internet Options → LAN Settings** and uncheck the proxy, or relaunch the app (it disables the proxy on startup). The app also auto-disables the proxy via `atexit` handlers. |
| Certificate not trusted / HTTPS errors | Re-run `mitmproxy`, visit `http://mitm.it`, and reinstall the certificate |
| No telemetry data appearing | Make sure Sea of Thieves is running **after** clicking Start Capture — the game must establish connections through the proxy |
| `mitmdump` not found | Ensure mitmproxy is installed and its binary is on your system PATH |
| Dashboard shows stale data | Check the "Last Updated" timestamps on each panel — some telemetry events are sent infrequently by the game |

---

## Credits

Forked from the original project by [**InsaneSoftware**](https://github.com/InsaneSoftware/Sot-Client-Scanner).

---

## Disclaimer

This project:

- Does **not** modify the game
- Does **not** inject into game memory
- Only observes outbound telemetry traffic
- Intended for educational and research use

Use responsibly.
