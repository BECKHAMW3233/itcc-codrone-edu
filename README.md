# ITCC CoDrone EDU Flight Programming

Information Technology Cyber Club (ITCC) project repo for programming
CoDrone EDU flight missions in Python.

## What this repo is

A shared codebase where club members write, test, and submit flight
programs for the CoDrone EDU. Each mission is a self-contained Python
script that controls a drone from takeoff through a planned flight
path (specific altitudes, patterns, tasks) and back to landing —
either at the original takeoff point or a separate designated landing
location, optionally followed by a return takeoff.

## Hardware / software requirements

- CoDrone EDU drone + USB Bluetooth dongle
- Python 3.8+
- `codrone-edu` Python package: `pip install codrone-edu`
- A well-lit, patterned flying surface (needed for the drone's optical
  flow sensor to track distance accurately)
- Battery charged above 50% before flying — flight commands can fail
  silently below that

## Repo layout

```
itcc-codrone-repo/
├── README.md              - this file
├── CONTRIBUTING.md         - how to submit a mission
├── missions/               - individual member flight-path scripts
│   └── altitude_square_demo.py   - example: staged altitude climb + square pattern
├── scripts/                - shared/reusable helper code (empty for now)
└── docs/                   - reference notes, SDK function summaries, etc.
```

This is a starting skeleton. As the club adds more missions, we'll
likely reorganize `missions/` further (e.g. by member, by semester,
or by task type) — see CONTRIBUTING.md for the current submission
process.

## Quick start

```bash
pip install codrone-edu
python missions/altitude_square_demo.py
```

Always test new mission scripts with the propellers off first if
you're unsure about the logic, and have a clear, obstacle-free flight
area before running anything with propellers attached.

## Safety notes

- Never fly over people or pets.
- Keep a clear line of sight to the drone at all times.
- Know where `drone.land()` and `drone.emergency_stop()` are in your
  script before you run it.
- Battery level, propeller condition, and floor lighting/pattern all
  affect flight accuracy — check these before every flight.
