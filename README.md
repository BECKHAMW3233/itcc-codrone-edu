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

**New to this repo?** See
[`docs/getting-access-and-setup.md`](docs/getting-access-and-setup.md)
for how to get added as a collaborator and set everything up locally.

**New to Python, or a non-programmer joining the club?** See
[`docs/python-concepts-guide.md`](docs/python-concepts-guide.md)
first — it explains the Python patterns (functions, tuples, loops,
try/finally) used throughout `missions/`, in plain language with
small examples, before you try reading the mission scripts
themselves.

## Hardware / software requirements

- CoDrone EDU drone + USB Bluetooth dongle
- Python 3.8+
- `codrone-edu` Python package — install with:
  ```bash
  pip install -r requirements.txt
  ```
- A well-lit, patterned flying surface (needed for the drone's optical
  flow sensor to track distance accurately)
- Battery charged above 50% before flying — flight commands can fail
  silently below that

## Repo layout

```
itcc-codrone-edu/
├── README.md                    - this file
├── CONTRIBUTING.md              - how to submit a mission
├── requirements.txt             - Python package dependencies
├── .github/workflows/            - CI: automated syntax check on push/PR
│   └── syntax-check.yml
├── codrone-edu-resources/       - links to Robolink's official manual, API docs, and specs
│   └── README.md
├── missions/                    - individual member flight-path scripts
│   ├── altitude_square_demo.py     - staged altitude climb (cm) + square pattern
│   ├── grid_flight_plan.py         - 2D grid navigation (X/Y, cm-based)
│   ├── grid_3d_flight_plan.py      - 3D grid navigation (X/Y/altitude, cm-based)
│   └── waypoint_route.py           - waypoint-based route: diagonal moves + heading turns
├── scripts/                     - shared/reusable helper code
│   └── converter.py                - interactive inches/feet <-> cm/meters converter
└── docs/                        - reference notes, SDK function summaries, etc.
    ├── getting-access-and-setup.md - how to get repo access + set up locally
    ├── python-concepts-guide.md    - plain-language Python concepts used in missions/
    ├── sdk-quick-reference.md      - CoDrone EDU Python SDK cheat sheet
    ├── using-claude-code.md        - optional: using Claude Code locally to edit files and manage Git here
    └── using-claude-code-online.md - optional: using Claude Code online (claude.ai/code) with this repo's GitHub
```

This is a starting skeleton. As the club adds more missions, we'll
likely reorganize `missions/` further (e.g. by member, by semester,
or by task type) — see CONTRIBUTING.md for the current submission
process.

## What's here so far

**Mission scripts** (`missions/`) — all four are configured in
centimeters. The first three call SDK functions that natively accept
cm directly. `waypoint_route.py` is configured in cm too, for
consistency, but converts to meters internally since its underlying
SDK function (`send_absolute_position()`) only accepts meters — you
never need to do that conversion yourself.

- `altitude_square_demo.py` — climbs in 15.24 cm (6 in) steps up to
  152.4 cm (5 ft), hovering 5 seconds at each step, and flies a
  30.48 cm (12 in) square pattern when it passes through 91.44 cm (3 ft).
- `grid_flight_plan.py` — navigates a 2D grid of 30.48 cm squares to
  a target (x, y) location and back, using only 15.24 cm movement
  increments.
- `grid_3d_flight_plan.py` — same grid navigation, plus a Z axis:
  climbs to a target altitude (in 15.24 cm steps) before crossing the
  grid, then reverses the whole trip to land back at the start.
- `waypoint_route.py` — a genuine waypoint-based route, unlike the
  three scripts above. Instead of chaining single-axis moves into an
  L-shaped path, this flies a list of absolute (x, y, z, heading)
  waypoints using `send_absolute_position()`, moving diagonally in
  3D and turning to a specific heading at each stop. This is the
  right starting point for a mission that needs to climb, descend,
  turn, and move forward in a new direction — not just a fixed shape.

Every mission script wraps its flight logic in `try`/`finally` so the
drone lands and the connection closes even if something goes wrong
mid-flight.

**⚠️ Status: none of the mission scripts have been flown on hardware
yet.** They're written against the documented SDK but need real
test flights before the club relies on them. See each script's
module docstring for a specific list of known limitations.

**Utility scripts** (`scripts/`):

- `converter.py` — a small interactive command-line tool for
  converting distances between inches/feet and cm/meters. Useful when
  planning a flight in feet/inches but needing cm values for a
  mission script's configuration. This one has been tested and works
  correctly.

**Docs** (`docs/`):

- `getting-access-and-setup.md` — how to get added to the repo as a
  collaborator and set up the project locally. Start here if you're
  new.
- `python-concepts-guide.md` — plain-language explanations of the
  Python patterns used across `missions/` (functions, docstrings,
  tuples, loops, default arguments, try/finally). Read this before
  the mission scripts if you're newer to Python — every mission file
  links back to it instead of re-explaining these ideas each time.
- `sdk-quick-reference.md` — a cheat sheet of commonly used CoDrone
  EDU Python SDK functions (takeoff/land, movement, altitude,
  sensors), verified against Robolink's official documentation.
- `using-claude-code.md` — optional guide for members who want to use
  the Claude Code AI assistant to edit files and handle Git
  (clone/pull/push) in this repo, written for someone who has never
  opened Claude Code before.
- `using-claude-code-online.md` — companion guide for the browser-only
  version of Claude Code (claude.ai/code), connected directly to
  GitHub with nothing installed locally. Can't test-fly the drone
  (no local hardware access) but covers everything else, including
  opening pull requests from a phone.

**Official resources** (`codrone-edu-resources/`):

- Links to Robolink's own CoDrone EDU user manual, Python API
  documentation, technical specs, and support — see
  [`codrone-edu-resources/README.md`](codrone-edu-resources/README.md).
  These are Robolink's materials, linked rather than copied into this
  repo.

**CI** (`.github/workflows/syntax-check.yml`):

Every push and pull request automatically checks that all Python
files compile and every mission script defines a `main()` function.
It doesn't test actual flight behavior (that needs real hardware),
just catches broken syntax before it merges. `main` is protected, so
all changes — including from collaborators — go through a pull
request and this check.

## Quick start

```bash
pip install -r requirements.txt

# run the distance converter (no drone required)
python scripts/converter.py

# run a mission (drone required, paired via USB dongle)
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
- No mission script in this repo currently checks room size or
  ceiling height against the distances it's about to fly — measure
  your space and compare it to the script's configured distances
  before running anything.
