"""
CoDrone EDU - Waypoint Mission Runner
==================================================================

STATUS: UNTESTED ON HARDWARE. This script has been written against
the documented CoDrone EDU Python SDK but has not yet been flown.
Test in a clear, obstacle-free space at low speed, and be ready to
hit drone.land() / drone.emergency_stop() manually if it behaves
unexpectedly.

WHAT THIS SCRIPT DOES (AND WHY IT'S DIFFERENT FROM THE OTHER MISSIONS)
------------------------------------------------------------------------
The other scripts in this folder (grid_flight_plan.py,
grid_3d_flight_plan.py, altitude_square_demo.py) all move the drone
by chaining single-axis calls like move_forward()/move_left() one
after another. That produces "L-shaped" paths only - the drone
completes an entire forward/backward move, THEN an entire left/right
move, never both at once, and it never changes its own facing
direction (heading).

This script instead defines a MISSION as a list of WAYPOINTS - each
one a specific (x, y, z, heading) target - and flies to each waypoint
in order using send_absolute_position(), which:
  - moves in a straight line toward the target X/Y/Z position
    (true diagonal/3D movement in one command, not an L-shaped path)
  - simultaneously rotates the drone to a specific heading on arrival
  - uses ABSOLUTE coordinates from the takeoff point, not relative
    "move forward N cm from wherever I currently am" commands

This is the right building block for a route that climbs, descends,
turns, and moves forward again in a new direction - the kind of
"proper" pre-planned flight path a real mission needs, instead of a
single hardcoded shape.

COORDINATE SYSTEM AND UNITS
------------------------------
  - Every waypoint is defined in CENTIMETERS (cm) in this script's
    WAYPOINTS list, to stay consistent with every other script in
    this repo - but send_absolute_position() itself only accepts
    METERS, so this script converts cm -> meters automatically before
    calling the SDK. You never need to do that conversion yourself.
  - Coordinates are ABSOLUTE, measured from the drone's takeoff point
    at (0, 0, 0) - NOT relative to the previous waypoint. Waypoint 2
    at (100, 0, 50) means "100cm forward of takeoff, 50cm up," not
    "100cm forward of waypoint 1."
  - X = forward(+)/backward(-) from takeoff, in cm
    Y = left(+)/right(-) from takeoff, in cm
      NOTE: this follows the SDK's own send_absolute_position() sign
      convention as documented, which may differ from the "right is
      positive" convention used in this repo's other grid scripts -
      double check against the official docs before assuming.
    Z = altitude in cm from the ground at takeoff
    heading = absolute compass-style heading in degrees the drone
      should be facing once it ARRIVES at this waypoint (0 = the
      direction the drone was facing at takeoff)
  - Because every waypoint is absolute and send_absolute_position()
    handles the turn AND the move together, this script does NOT
    need to track "which way is the drone currently facing" itself -
    that bookkeeping problem (and the heading-drift trap that
    move_distance() has - see WHY send_absolute_position(), not
    move_distance() below) is handled by the SDK.

WHY send_absolute_position(), NOT move_distance()
-----------------------------------------------------
The SDK also has move_distance(x, y, z, velocity), which moves all
three axes simultaneously - but it is RELATIVE to the drone's CURRENT
position AND CURRENT HEADING. Per Robolink's own sensor
documentation: if the drone's heading is not 0 (i.e. it has turned
since takeoff), "left/right movement no longer solely changes
y-position and forward/backward no longer solely changes x-position."

That means chaining move_distance() calls across a route that
includes turns would require this script to manually track the
drone's current heading and rotate each subsequent move's x/y values
to account for it - an easy place to introduce a silent bug.
send_absolute_position() avoids this entirely by always working in
the fixed world/takeoff frame, regardless of which way the drone is
currently facing. This is why the waypoint runner is built on
send_absolute_position() instead.

PSEUDOCODE
-----------
    connect to drone
    take off
    hover briefly

    for each waypoint (x_cm, y_cm, z_cm, heading, label) in WAYPOINTS:
        convert x_cm, y_cm, z_cm to meters
        call send_absolute_position(x_m, y_m, z_m, velocity,
                                     heading, rotational_velocity)
        hover at this waypoint for HOVER_SECONDS
        print which waypoint was reached

    land
    close connection

KNOWN LIMITATIONS
-------------------
  - This is the LEAST tested design in this repo - it depends on
    send_absolute_position() behaving exactly as documented,
    including its coordinate sign convention, which has not been
    verified against real hardware. Test extremely cautiously.
  - No bounds/obstacle checking - nothing stops a waypoint from being
    set outside your actual flying space, or above your ceiling
    height. Measure your space and compare against every waypoint's
    x/y/z before running this.
  - send_absolute_position() needs a well-lit, patterned surface for
    the optical flow sensor to track absolute position accurately -
    drift is more likely to compound here than in the simpler
    single-axis scripts, since errors in position tracking accumulate
    across every waypoint in the route.
  - This script does not verify it actually arrived at a waypoint
    before moving to the next one (e.g. by checking get_position_data()
    against the target) - it simply issues the command, hovers for a
    fixed time, and moves on. A club member extending this could add
    a position-check loop similar to the altitude-climb pattern used
    in altitude_square_demo.py.
  - The Y-axis sign convention (left vs. right as positive) should be
    confirmed against a real test flight before trusting the exact
    left/right direction of any waypoint route - the docstring above
    flags this as unconfirmed.

Usage:
    Edit the WAYPOINTS list below - each entry is
    (x_cm, y_cm, z_cm, heading_degrees, label) - and run.

NEW TO PYTHON? READ THIS FIRST
---------------------------------
If terms like "function," "docstring," "tuple," or "try/finally"
below aren't familiar yet, see docs/python-concepts-guide.md in this
repo first - it specifically covers tuples and "unpacking" a tuple in
a for loop, both of which are used heavily in this file (the
WAYPOINTS list below is a list of tuples, and fly_waypoint_route()
unpacks each one).
"""

from codrone_edu.drone import *

# ---------------- Configuration ----------------
CM_TO_M = 1 / 100             # convert cm -> meters (SDK's native unit for these calls)

VELOCITY_MS = 0.5             # m/s for each waypoint-to-waypoint move
ROTATIONAL_VELOCITY_DEG_PER_SEC = 90   # degrees/second for turns during each move
HOVER_SECONDS = 5             # hover time at every waypoint, including takeoff and the end

# Each waypoint is a TUPLE - a small fixed group of values - holding:
#   (x_cm, y_cm, z_cm, heading_degrees, label)
#   x_cm, y_cm, z_cm - ABSOLUTE position in cm from the takeoff point (0,0,0)
#   heading_degrees  - absolute heading the drone should face on arrival
#   label            - a human-readable name for this waypoint, used in print statements
#
# WAYPOINTS itself is a LIST of these tuples - one tuple per stop on
# the route, in the order they should be flown. See
# docs/python-concepts-guide.md if "tuple" and "list of tuples" are
# new terms.
#
# Example route: climb and move forward, turn right and move sideways,
# descend partway while turning again, then return toward start.
WAYPOINTS = [
    (100, 0,   80, 0,   "Waypoint 1: 100cm forward, 80cm altitude, facing forward"),
    (100, 100, 80, 90,  "Waypoint 2: 100cm left of start, same altitude, facing right"),
    (50,  100, 50, 180, "Waypoint 3: descending to 50cm, facing backward"),
    (0,   0,   80, 0,   "Waypoint 4: back to start position, climbed to 80cm, facing forward"),
]


def fly_to_waypoint(drone, x_cm, y_cm, z_cm, heading, label,
                     velocity_ms=VELOCITY_MS,
                     rotational_velocity=ROTATIONAL_VELOCITY_DEG_PER_SEC,
                     hover_seconds=HOVER_SECONDS):
    """
    Fly to a single absolute waypoint and hover once arrived.

    IN PLAIN LANGUAGE: this function takes one waypoint's worth of
    information (a position and a heading) and sends it to the drone
    in one command. The drone's onboard flight controller then
    figures out how to actually get there - this function doesn't
    calculate the path itself, it just hands off the destination and
    lets send_absolute_position() handle the flying.

    Pseudocode:
        convert x_cm, y_cm, z_cm to meters (SDK requires meters)
        call send_absolute_position(x_m, y_m, z_m, velocity_ms,
                                     heading, rotational_velocity)
        hover for hover_seconds
        print confirmation with the waypoint's label

    Args (the information this function needs to run):
        drone: the connected Drone instance.
        x_cm (float): absolute X position in cm from takeoff.
        y_cm (float): absolute Y position in cm from takeoff.
        z_cm (float): absolute Z (altitude) position in cm from takeoff.
        heading (float): absolute heading in degrees to face on arrival.
        label (str): human-readable name for this waypoint, used in
            print statements only - not sent to the drone.
        velocity_ms (float): speed in m/s for this move. Has a
            default value (VELOCITY_MS) so you don't have to specify
            it every time you call this function - see
            docs/python-concepts-guide.md section on default argument
            values if that's unfamiliar.
        rotational_velocity (float): turn speed in degrees/second.
        hover_seconds (float): how long to hover once arrived.

    Returns (what comes back out of this function):
        None - this function doesn't hand back a value, it just moves
        the drone and leaves it hovering at the target waypoint,
        facing the target heading.
    """
    x_m = x_cm * CM_TO_M
    y_m = y_cm * CM_TO_M
    z_m = z_cm * CM_TO_M

    print(f"Flying to {label} -> ({x_cm}cm, {y_cm}cm, {z_cm}cm), heading {heading} deg")
    drone.send_absolute_position(x_m, y_m, z_m, velocity_ms, heading, rotational_velocity)

    print(f"  Arrived. Hovering {hover_seconds}s.")
    drone.hover(hover_seconds)


def fly_waypoint_route(drone, waypoints):
    """
    Fly through an entire list of waypoints in order, calling
    fly_to_waypoint() for each one.

    IN PLAIN LANGUAGE: `waypoints` is a list of tuples (see WAYPOINTS
    above). The line `for x_cm, y_cm, z_cm, heading, label in
    waypoints:` below loops over that list one tuple at a time, and
    on each pass it "unpacks" that one tuple's five values into five
    separate variable names - x_cm, y_cm, z_cm, heading, label - so
    they can be handed individually to fly_to_waypoint(). See
    docs/python-concepts-guide.md for more on tuple unpacking if this
    line looks unfamiliar.

    Pseudocode:
        for each waypoint in the list:
            unpack (x_cm, y_cm, z_cm, heading, label)
            fly_to_waypoint(drone, x_cm, y_cm, z_cm, heading, label)

    Args (the information this function needs to run):
        drone: the connected Drone instance.
        waypoints (list): list of (x_cm, y_cm, z_cm, heading, label)
            tuples, in the order they should be flown.

    Returns (what comes back out of this function):
        None - this function doesn't hand back a value, it just flies
        the whole route, one waypoint at a time, in order.
    """
    for x_cm, y_cm, z_cm, heading, label in waypoints:
        fly_to_waypoint(drone, x_cm, y_cm, z_cm, heading, label)


def main():
    """
    Entry point. Connects to the drone and flies the full WAYPOINTS
    route defined above, landing at the end regardless of whether an
    error occurs partway through.

    Pseudocode:
        create Drone object and pair
        take off, hover at start
        try:
            fly_waypoint_route(WAYPOINTS)
        finally:
            land
            close the connection
    """
    drone = Drone()
    drone.pair()

    drone.takeoff()
    print("Takeoff complete. Hovering at start (0, 0, 0).")
    drone.hover(HOVER_SECONDS)

    try:
        fly_waypoint_route(drone, WAYPOINTS)
        print("Waypoint route complete.")
    finally:
        print("Landing.")
        drone.land()
        drone.close()


if __name__ == "__main__":
    main()
