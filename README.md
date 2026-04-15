# HumidiZone - Smart Humidity Control System
### University Module U19969 | Smart Systems Assignment

---

## Overview
HumidiZone is a Python-based smart humidity control system designed to monitor and manage humidity levels across four greenhouse zones. The system uses simulated sensor nodes, a SQLite database for data logging, and a Tkinter-based GUI dashboard.

---

## Zones
| Zone | Name | Min Humidity | Max Humidity |
|------|------|-------------|-------------|
| 1 | Propagation | 70% | 80% |
| 2 | Vegetation | 60% | 70% |
| 3 | Flowering | 40% | 60% |
| 4 | Storage | 50% | 65% |

---

## System Architecture
- **main.py** - Entry point. Initialises database tables and launches frontend
- **frontend.py** - Tkinter GUI dashboard
- **processing.py** - Reads sensor data and compares against thresholds
- **actuation.py** - Makes actuation decisions and logs energy consumption
- **Simulation.py** - DEV ONLY. Simulates sensor feed (replace with real hardware)
- **presentation.py** - Legacy terminal menu, superseded by frontend.py
- **zones.json** - Zone configuration file
- **humidity.db** - SQLite database
- **password.txt** - Temporary authentication password storage

---

## Requirements
- Python 3.x
- Tkinter (built into Python)
- SQLite3 (built into Python)

---

## Running the System
```bash
python main.py
```

---

## GUI - Frontend
The frontend is built using Tkinter, Python's built-in GUI library. It provides:

### Main Window
- **Header** - System title and online/offline status indicator
- **Live Readings Panel** - Displays current humidity per zone, colour coded green (in range) or red (out of range)
- **Actuation Status Panel** - Displays current actuator state per zone (IDLE / HUMIDIFIER ON / DEHUMIDIFIER ON)
- **Control Buttons** - Start System, Stop System, Quit

### Admin Controls
Admin features are hidden by default and require authentication to access.
- **Login** - Click "Login as Admin" and enter the admin password
- **Adjust Thresholds** - Modify min/max humidity thresholds per zone
- **Manual Override** - Manually force actuator state per zone (non-functional in current build)
- **Logout** - Hides admin controls

### Authentication
Authentication uses a local password file (`password.txt`). This is for development purposes only and should be replaced with a secure authentication system in production.

---

## Database Tables
| Table | Description |
|-------|-------------|
| zoneN_name | Humidity readings per zone |
| logActions | System startup, interrupt and quit events |
| logActuation | Actuation decisions per zone per cycle |
| logEnergy | Energy consumption per zone per cycle |
| logAdjust | Threshold adjustment history |

---

## Development Notes
- `Simulation.py` is a DEV ONLY component that generates random humidity values to simulate a real sensor feed. It should be replaced with real sensor hardware integration in production.
- `password.txt` is excluded from version control. Default password is `admin123`.
- Zone profiles are loaded dynamically from `zones.json` - adding or modifying zones here propagates through the whole system.

---

## Known Limitations
- Simulation generates random values and does not respond to actuation commands
- Authentication is file-based and not suitable for production
- No physical actuators - actuation decisions are logged only

---

## Authors
**Harry Pert** ,
**Jake Dinning** ,
**Tom Lunenborg**
*Group Assignment - Module U19969*
