"""
CoDrone EDU - Grid + Altitude Navigation Flight Plan (3D)
==================================================================

STATUS: UNTESTED ON HARDWARE. This script has been written against
the documented CoDrone EDU Python SDK but has not yet been flown.
The negative-throttle descent logic in particular is a best guess
based on how throttle is documented to work, not a confirmed-working
technique. Test in a clear, obstacle-free space at low
throttle/speed, and be ready to hit drone.land() /
drone.emergency_stop() manually if it behaves unexpectedly.

WHAT THIS MISSION DOES
-----------------------
Navigates the drone to a 3D target defined as (x_grid, y_grid,
z_steps), climbing to altitude first, then moving horizontally, then
reversing both to return to the takeoff point before landing.

COORDINATE SYSTEM (IMPORTANT: X/Y and Z use DIFFERENT units)
----------------------------------------------------------------
  x_grid   - grid squares forward(+)/backward(-). 1 grid square = 30.48 cm.
  y_grid   - grid squares right(+)/left(-).       1 grid square = 30.48 cm.
  z_steps  - altitude in 15.24 cm INCREMENTS directly (NOT grid squares).
             e.g. z_steps = 5 means 5 * 15.24cm = 76.2 cm of hover height.

  Example target (10, 6, 5):
    - 10 grid squares forward = 304.8 cm forward
    - 6 grid squares right    = 182.88 cm right
    - 5 altitude steps        = 76.2 cm hover height

  (These cm values correspond to a flight plan originally specified
  in inches: 12-inch grid squares navigated in 6-inch horizontal
  steps, with altitude directly in 6-inch increments. All units here
  are cm to match the SDK natively.)

  All horizontal movement (X/Y) is flown in 15.24 cm physical
  increments (two 15.24cm moves per 30.48cm grid square) - same rule
  as the 2D grid_flight_plan.py script. Altitude uses 15.24 cm
  increments directly; there is no "grid square" concept on the Z axis.

FLIGHT SEQUENCE
-----------------
  1. Take off, hover at (0, 0, 0).
  2. Climb to the target altitude (z_steps * 15.24 cm), hover.
  3. Fly horizontally to (x_grid, y_grid) at that altitude, hover.
  4. Return horizontally to (0, 0) at the same altitude, hover.
  5. Descend back to takeoff height, hover.
  6. Land.

  Climb happens BEFORE horizontal movement (not simultaneously). The
  drone gains all its altitude first, then crosses the grid at a
  constant height, rather than climbing and moving at the same time.

PSEUDOCODE
-----------
    connect to drone
    take off
    hover at (0, 0, 0) for 5 seconds

    read target (x_grid, y_grid, z_steps), e.g. (10, 6, 5)

    # --- outbound: climb, then move horizontally ---
    climb_by_steps(z_steps):
        target_altitude = current_altitude + (z_steps * 15.24 cm)
        set throttle up (or down, if z_steps is negative)
        loop: move() + check get_height("cm"), until within tolerance
        set throttle to 0
    hover 5 seconds at target altitude

    fly_horizontal(x_grid, y_grid):            # same logic as 2D script
        if x_grid is not zero:
            repeat (|x_grid| * 2) times: move forward/backward 15.24 cm
        if y_grid is not zero:
            repeat (|y_grid| * 2) times: move right/left 15.24 cm
    hover 5 seconds at (x_grid, y_grid, z_steps)

    # --- return: reverse horizontal, then reverse climb ---
    fly_horizontal(-x_grid, -y_grid)
    hover 5 seconds back over (0, 0), still at altitude

    climb_by_steps(-z_steps)                    # descend back down
    hover 5 seconds at (0, 0, 0)

    land
    close connection

KNOWN LIMITATIONS
-------------------
  - Descending uses negative throttle (-CLIMB_THROTTLE). This is a
    reasonable assumption based on how throttle is generally
    documented, but has NOT been confirmed against the actual SDK
    behavior on hardware. Verify this works as expected before
    trusting it for a real descent.
  - No bounds/obstacle checking on any axis, including altitude -
    nothing stops z_steps from being set higher than your ceiling
    allows. Measure your space (including height) before choosing
    target coordinates.
  - Climbs fully before moving horizontally (not simultaneous, not
    diagonal). If a mission needs the drone to gain altitude while
    also moving across the grid, that requires different logic than
    what's here.
  - move_forward/backward/left/right() rely on the optical flow
    sensor. Fly over a well-lit, patterned surface for best accuracy.
  - ALL horizontal distances and speeds in this script are in
    centimeters (cm) and centimeters/second, matching the units the
    CoDrone EDU SDK natively accepts. Speed is converted to
    meters/second only at the point of the actual SDK call. Max SDK
    speed is 2.0 m/s (200 cm/sec). This does NOT affect climb/descend
    rate, which is controlled separately by CLIMB_THROTTLE (a
    throttle percentage, not a speed) since altitude changes use
    set_throttle(), not the distance-based move functions.

Usage:
    Edit TARGET_3D below (or call
    fly_to_3d_grid(drone, x, y, z) directly with your own
    coordinates) and run.

NEW TO PYTHON? READ THIS FIRST
---------------------------------
If terms like "function," "docstring," "tuple," or "try/finally"
below aren't familiar yet, see docs/python-concepts-guide.md in this
repo first. This file builds on grid_flight_plan.py (same X/Y
stepping logic) and adds a Z axis on top - if move_axis_steps() below
is confusing, that function is explained more fully in
grid_flight_plan.py's docstring, since it's the same function reused
here.
"""

from codrone_edu.drone import *
import time

# ---------------- Configuration ----------------
GRID_SQUARE_CM = 30.48       # size of one grid square (X/Y), cm (= 12 inches)
MOVE_STEP_CM = 15.24         # every horizontal physical move, cm (= 6 inches)
STEPS_PER_GRID = round(GRID_SQUARE_CM / MOVE_STEP_CM)   # = 2 moves per grid square

ALTITUDE_STEP_CM = 15.24     # every altitude increment, cm (Z axis) (= 6 inches)

# Horizontal movement speed for each 15.24cm move, in cm/second.
# Converted to m/s below since that's the unit the SDK's move
# functions accept. Max SDK speed is 2.0 m/s (200 cm/sec). This
# does NOT control climb/descend rate - that's CLIMB_THROTTLE below.
MOVE_SPEED_CM_PER_SEC = 50    # cm per second
MOVE_SPEED_MS = MOVE_SPEED_CM_PER_SEC / 100   # cm/sec -> m/s

HOVER_SECONDS = 5            # hover time at every stop
CLIMB_THROTTLE = 40          # throttle % used while climbing
CLIMB_TOLERANCE_CM = 3       # how close (cm) to target before stopping climb

# Target location: (x_grid, y_grid, z_steps)
#   x_grid, y_grid -> grid squares (30.48cm each), X=fwd/back, Y=right/left
#   z_steps        -> 15.24cm altitude increments (NOT grid squares)
TARGET_3D = (10, 6, 5)   # 304.8cm forward, 182.88cm right, 76.2cm hover height


def move_axis_steps(drone, num_grid_squares, forward_func, backward_func, speed_ms):
    """
    Move along a single horizontal axis in 15.24 cm increments,
    covering a given number of 30.48 cm grid squares. Identical logic
    to the 2D grid script's version of this function.

    Pseudocode:
        total_steps = |num_grid_squares| * 2   # 2 moves of 15.24cm per grid square
        pick move_func = forward_func if num_grid_squares is positive,
                          else backward_func
        repeat total_steps times:
            call move_func(15.24 cm, speed_ms)
            print progress for this step

    Args:
        drone: the connected Drone instance.
        num_grid_squares (int): signed grid squares to cover on this
            axis. Sign picks the direction function; magnitude picks
            the distance.
        forward_func (callable): drone method for the positive
            direction (e.g. drone.move_forward, drone.move_right).
        backward_func (callable): drone method for the negative
            direction (e.g. drone.move_backward, drone.move_left).
        speed_ms (float): speed in m/s for each individual move.

    Returns:
        None.
    """
    total_steps = abs(num_grid_squares) * STEPS_PER_GRID
    move_func = forward_func if num_grid_squares > 0 else backward_func
    direction_label = "forward" if num_grid_squares > 0 else "backward"

    for step in range(total_steps):
        move_func(MOVE_STEP_CM, units="cm", speed=speed_ms)
        print(f"    step {step + 1}/{total_steps}: moved {MOVE_STEP_CM}cm {direction_label}")


def climb_by_steps(drone, z_steps):
    """
    Climb or descend by a number of 15.24 cm altitude steps, relative
    to the drone's CURRENT altitude (not an absolute height).

    IN PLAIN LANGUAGE: this is the same "throttle up, check the
    height sensor, stop when close enough" idea as climb_to() in
    altitude_square_demo.py, but this version can also go DOWN, not
    just up. The sign of z_steps decides the direction: a positive
    number (like 3) means climb, a negative number (like -3) means
    descend. This function uses POSITIVE throttle to climb and
    NEGATIVE throttle to descend - think of it like a video game
    control stick that goes up when pushed one way and down when
    pushed the other way. The loop condition
    (`while (climbing and ...) or (not climbing and ...)`) looks
    complicated, but it's really just "keep going until we're close
    enough to the target" checked in whichever direction we're
    actually moving.

    Pseudocode:
        if z_steps is 0: do nothing, return

        target_change = z_steps * 15.24 cm
        start_altitude = get_height("cm")
        target_altitude = start_altitude + target_change
        climbing = (z_steps > 0)

        set throttle = +CLIMB_THROTTLE if climbing else -CLIMB_THROTTLE
        loop:
            call move() to apply throttle for one tick
            re-read current altitude
            stop looping once within tolerance of target_altitude
                (comparison direction depends on climbing vs descending)
            small sleep between checks
        set throttle back to 0, call move() once to apply it

    Args (the information this function needs to run):
        drone: the connected Drone instance.
        z_steps (int): signed number of 15.24 cm altitude steps.
            Positive climbs, negative descends, 0 does nothing.

    Returns (what comes back out of this function):
        None - this function doesn't hand back a value, it just moves
        the drone up or down and leaves it hovering at approximately
        start_altitude + (z_steps * 15.24cm), within CLIMB_TOLERANCE_CM.
    """
    if z_steps == 0:
        return

    target_change_cm = z_steps * ALTITUDE_STEP_CM
    start_cm = drone.get_height("cm")
    target_cm = start_cm + target_change_cm

    climbing = z_steps > 0
    direction_label = "climbing" if climbing else "descending"
    print(f"  {direction_label} {abs(target_change_cm):.2f}cm "
          f"({abs(z_steps)} altitude step(s))...")

    drone.set_throttle(CLIMB_THROTTLE if climbing else -CLIMB_THROTTLE)
    current_cm = start_cm
    while (climbing and current_cm < target_cm - CLIMB_TOLERANCE_CM) or \
          (not climbing and current_cm > target_cm + CLIMB_TOLERANCE_CM):
        drone.move()
        current_cm = drone.get_height("cm")
        time.sleep(0.05)

    drone.set_throttle(0)
    drone.move()


def fly_horizontal(drone, x_grid, y_grid, speed_ms=MOVE_SPEED_MS):
    """
    Move horizontally to (x_grid, y_grid) relative to the drone's
    current position, without changing altitude. X-axis moves
    complete fully before Y-axis moves begin (taxicab path).

    Pseudocode:
        if x_grid is not zero:
            move_axis_steps() forward/backward for |x_grid| squares
        if y_grid is not zero:
            move_axis_steps() right/left for |y_grid| squares

    Args:
        drone: the connected Drone instance.
        x_grid (int): grid squares forward (+) or backward (-).
        y_grid (int): grid squares right (+) or left (-).
        speed_ms (float): speed in m/s for each 15.24 cm move.

    Returns:
        None.
    """
    if x_grid != 0:
        print(f"  X axis: {abs(x_grid)} grid square(s) "
              f"{'forward' if x_grid > 0 else 'backward'}")
        move_axis_steps(drone, x_grid, drone.move_forward, drone.move_backward, speed_ms)

    if y_grid != 0:
        print(f"  Y axis: {abs(y_grid)} grid square(s) "
              f"{'right' if y_grid > 0 else 'left'}")
        move_axis_steps(drone, y_grid, drone.move_right, drone.move_left, speed_ms)


def fly_to_3d_grid(drone, x_grid, y_grid, z_steps,
                    speed_ms=MOVE_SPEED_MS, hover_seconds=HOVER_SECONDS):
    """
    Fly from the drone's current position to a full 3D target:
    climb to the target altitude change first, THEN move horizontally
    to (x_grid, y_grid). Hovers after the climb and again after the
    horizontal move.

    Pseudocode:
        climb_by_steps(z_steps)
        hover for hover_seconds
        fly_horizontal(x_grid, y_grid)
        hover for hover_seconds

    Args:
        drone: the connected Drone instance.
        x_grid (int): grid squares forward (+) or backward (-).
        y_grid (int): grid squares right (+) or left (-).
        z_steps (int): 15.24 cm altitude steps to climb (+) or
            descend (-) before moving horizontally.
        speed_ms (float): speed in m/s for horizontal moves.
        hover_seconds (float): hover duration after climbing and
            after arriving at the horizontal target.

    Returns:
        None. Leaves the drone hovering at the 3D target.
    """
    print(f"Flying to 3D target ({x_grid}, {y_grid}, {z_steps})...")

    climb_by_steps(drone, z_steps)
    print(f"  Reached target altitude. Hovering {hover_seconds}s.")
    drone.hover(hover_seconds)

    fly_horizontal(drone, x_grid, y_grid, speed_ms=speed_ms)
    print(f"Arrived at ({x_grid}, {y_grid}, {z_steps}). Hovering {hover_seconds}s.")
    drone.hover(hover_seconds)


def return_to_start(drone, x_grid, y_grid, z_steps,
                     speed_ms=MOVE_SPEED_MS, hover_seconds=HOVER_SECONDS):
    """
    Return to (0, 0, 0): first fly back horizontally to (0, 0) while
    staying at the current altitude, THEN descend back to the
    original takeoff height. Mirrors fly_to_3d_grid() in reverse
    order (horizontal first, then vertical, since the outbound trip
    was vertical first, then horizontal).

    Pseudocode:
        fly_horizontal(-x_grid, -y_grid)   # reverse the outbound horizontal move
        hover for hover_seconds
        climb_by_steps(-z_steps)            # reverse the outbound climb (descend)
        hover for hover_seconds

    Args:
        drone: the connected Drone instance.
        x_grid (int): the X grid coordinate the drone is currently
            at (the function negates this to travel back).
        y_grid (int): the Y grid coordinate the drone is currently at.
        z_steps (int): the altitude steps the drone climbed to get
            here (the function negates this to descend back down).
        speed_ms (float): speed in m/s for horizontal moves.
        hover_seconds (float): hover duration after the horizontal
            return and after the descent.

    Returns:
        None. Leaves the drone hovering at approximately its original
        takeoff position and altitude.
    """
    print(f"Returning to start (0, 0) from ({x_grid}, {y_grid}, {z_steps})...")

    fly_horizontal(drone, -x_grid, -y_grid, speed_ms=speed_ms)
    print(f"  Back over start point, still at altitude. Hovering {hover_seconds}s.")
    drone.hover(hover_seconds)

    climb_by_steps(drone, -z_steps)
    print(f"  Descended back to takeoff height. Hovering {hover_seconds}s.")
    drone.hover(hover_seconds)


def main():
    """
    Entry point. Connects to the drone and runs the full 3D mission:
    takeoff, climb + fly to TARGET_3D, hover, reverse the trip back
    to (0, 0, 0), hover, then land.

    The flight logic runs inside a try/finally block: if anything
    raises an exception mid-flight (including during the climb or
    descent), the finally block still calls drone.land() and
    drone.close() so the drone doesn't get left airborne with no
    landing command issued - this matters especially here since the
    throttle-based climb/descent logic is the least-tested part of
    this script (see KNOWN LIMITATIONS above).

    Pseudocode:
        create Drone object and pair
        take off, hover 5 seconds at (0, 0, 0)
        try:
            fly_to_3d_grid(target_x, target_y, target_z)
                # climbs first, then moves horizontally, hovers at target
            return_to_start(target_x, target_y, target_z)
                # moves horizontally back, then descends, hovers at (0,0,0)
        finally:
            land
            close the connection
            (runs even if an exception occurred above)
    """
    drone = Drone()
    drone.pair()

    drone.takeoff()
    print("Location (0, 0, 0): hovering at start.")
    drone.hover(HOVER_SECONDS)

    target_x, target_y, target_z = TARGET_3D

    try:
        fly_to_3d_grid(drone, target_x, target_y, target_z)
        return_to_start(drone, target_x, target_y, target_z)
        print("Flight plan complete.")
    finally:
        print("Landing.")
        drone.land()
        drone.close()


if __name__ == "__main__":
    main()
