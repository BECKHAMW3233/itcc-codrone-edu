"""
CoDrone EDU - Grid Navigation Flight Plan (2D)
==================================================================

STATUS: UNTESTED ON HARDWARE. This script has been written against
the documented CoDrone EDU Python SDK but has not yet been flown.
Test it in a clear, obstacle-free space at low speed before relying
on it, and be ready to hit drone.land() / drone.emergency_stop()
manually if it behaves unexpectedly.

WHAT THIS MISSION DOES
-----------------------
Navigates the drone across a grid of 30.48 x 30.48 cm squares, using
ONLY 15.24 cm physical movement increments (two 15.24cm moves = one
grid square on any axis). Takes off at grid location (0, 0), flies to
a target grid location, hovers there, and retraces the same path
back to (0, 0) before landing.

(These cm values correspond to a grid originally specified in
inches: 12-inch grid squares navigated in 6-inch movement
increments. All units here are cm to match the SDK natively - see
COORDINATE SYSTEM below.)

COORDINATE SYSTEM
-------------------
  - Units are GRID SQUARES, not cm directly. Each grid square = 30.48 cm.
  - X axis = forward (+) / backward (-)
  - Y axis = right (+) / left (-)
  - Location (0, 0) is the takeoff point.

  Example: target (10, -6) means:
    - 10 grid squares forward = 10 * 30.48 = 304.8 cm forward
    - 6 grid squares left     = 6 * 30.48  = 182.88 cm left (negative Y = left)

  Because every physical move must happen in 15.24 cm increments,
  each grid square of distance is flown as TWO 15.24 cm moves, never
  one 30.48 cm move. This keeps every single move() call in the
  flight log at a consistent step size - useful for tracking/verifying
  position along the way (e.g. with sensors, or for teaching
  step-by-step navigation logic).

  This script flies an "L-shaped" (taxicab) path: it completes the
  entire X-axis movement first, then the entire Y-axis movement. It
  does not move diagonally and does not interleave X/Y steps.

PSEUDOCODE
-----------
    connect to drone
    take off
    hover at (0, 0) for 5 seconds

    read target (x_grid, y_grid), e.g. (10, -6)

    # --- fly to target ---
    if x_grid is not zero:
        direction = forward if x_grid > 0 else backward
        repeat (|x_grid| * 2) times:      # 2 moves of 15.24cm per grid square
            move direction 15.24 cm
    if y_grid is not zero:
        direction = right if y_grid > 0 else left
        repeat (|y_grid| * 2) times:
            move direction 15.24 cm
    hover at (x_grid, y_grid) for 5 seconds

    # --- return to start (reverse path, negated coordinates) ---
    if x_grid is not zero:
        repeat (|x_grid| * 2) times:
            move opposite direction 15.24 cm
    if y_grid is not zero:
        repeat (|y_grid| * 2) times:
            move opposite direction 15.24 cm
    hover at (0, 0) for 5 seconds

    land
    close connection

KNOWN LIMITATIONS
-------------------
  - No bounds/obstacle checking - a large TARGET_GRID value will
    happily try to fly the drone into a wall if the room isn't big
    enough. Measure your space before choosing target coordinates.
  - move_forward/backward/left/right() rely on the optical flow
    sensor. Fly over a well-lit, patterned surface for best accuracy.
  - Flies X fully, then Y fully (L-shaped path) - not diagonal, not
    interleaved. If a club project needs an interleaved/zigzag path,
    that requires different move-ordering logic than what's here.
  - ALL distances and speeds in this script are in centimeters (cm)
    and centimeters/second, matching the units the CoDrone EDU SDK
    natively accepts. Speed is converted to meters/second only at
    the point of the actual SDK call. Max SDK speed is 2.0 m/s
    (200 cm/sec) - values above that will likely be clamped or
    rejected by the drone firmware.

Usage:
    Edit TARGET_GRID below (or call fly_to_grid(drone, x, y) directly
    with your own coordinates) and run.

NEW TO PYTHON? READ THIS FIRST
---------------------------------
If terms like "function," "docstring," "tuple," or "try/finally"
below aren't familiar yet, see docs/python-concepts-guide.md in this
repo before reading further. One thing in THIS file that guide
doesn't fully prepare you for: move_axis_steps() below takes actual
functions (like drone.move_forward) as arguments, not just numbers or
text - this lets the same code handle both the X axis and the Y axis
without writing near-duplicate code for each one. See that function's
docstring for a plain-language explanation.
"""

from codrone_edu.drone import *
import time

# ---------------- Configuration ----------------
GRID_SQUARE_CM = 30.48       # size of one grid square, cm (= 12 inches)
MOVE_STEP_CM = 15.24         # every physical move is in this increment (= 6 inches)
STEPS_PER_GRID = round(GRID_SQUARE_CM / MOVE_STEP_CM)   # = 2 moves per grid square

# Movement speed for each 15.24cm move, in cm/second. Converted to
# m/s below since that's the unit the SDK's move functions accept.
# Max SDK speed is 2.0 m/s (200 cm/sec).
MOVE_SPEED_CM_PER_SEC = 50    # cm per second
MOVE_SPEED_MS = MOVE_SPEED_CM_PER_SEC / 100   # cm/sec -> m/s

HOVER_SECONDS = 5            # hover time at start, target, and return-to-start

# Target grid location relative to start (0, 0).
# X = forward(+)/backward(-) grid squares, Y = right(+)/left(-) grid squares
TARGET_GRID = (10, -6)


def move_axis_steps(drone, num_grid_squares, forward_func, backward_func, speed_ms):
    """
    Move along a single axis in 15.24 cm increments, covering a given
    number of 30.48 cm grid squares.

    IN PLAIN LANGUAGE: this one function handles BOTH the X axis
    (forward/backward) and the Y axis (left/right), instead of
    writing two nearly-identical functions. It does this by taking
    the actual movement commands themselves as arguments -
    forward_func and backward_func - rather than always calling
    drone.move_forward()/drone.move_backward() by name inside the
    function. When this function is used for the X axis, the caller
    passes in drone.move_forward and drone.move_backward; when it's
    used for the Y axis, the caller passes in drone.move_right and
    drone.move_left instead. This is called "passing a function as an
    argument" - it's a more advanced pattern than passing numbers or
    text, but it's what avoids writing the same stepping logic twice.

    Pseudocode:
        total_steps = |num_grid_squares| * 2   # 2 moves of 15.24cm per grid square
        pick move_func = forward_func if num_grid_squares is positive,
                          else backward_func
        repeat total_steps times:
            call move_func(15.24 cm, speed_ms)
            print progress for this step

    Args (the information this function needs to run):
        drone: the connected Drone instance.
        num_grid_squares (int): signed number of grid squares to
            cover on this axis. Sign determines direction (which of
            forward_func/backward_func gets called); magnitude
            determines distance.
        forward_func (callable): the drone method to call for the
            positive direction (e.g. drone.move_forward or
            drone.move_right). "callable" just means "a function that
            can be called" - it's being handed in as data, not run yet.
        backward_func (callable): the drone method to call for the
            negative direction (e.g. drone.move_backward or
            drone.move_left).
        speed_ms (float): speed in m/s for each individual move.

    Returns (what comes back out of this function):
        None - this function doesn't hand back a value, it just moves
        the drone step by step and prints progress as it goes.
    """
    total_steps = abs(num_grid_squares) * STEPS_PER_GRID
    move_func = forward_func if num_grid_squares > 0 else backward_func
    direction_label = "forward" if num_grid_squares > 0 else "backward"

    for step in range(total_steps):
        move_func(MOVE_STEP_CM, units="cm", speed=speed_ms)
        print(f"    step {step + 1}/{total_steps}: moved {MOVE_STEP_CM}cm {direction_label}")


def fly_to_grid(drone, x_grid, y_grid, speed_ms=MOVE_SPEED_MS, hover_seconds=HOVER_SECONDS):
    """
    Fly from the drone's current position to a target grid location,
    moving the full X-axis distance first, then the full Y-axis
    distance (an L-shaped / taxicab path, not diagonal).

    Pseudocode:
        if x_grid is not zero:
            move_axis_steps() along forward/backward for |x_grid| squares
        if y_grid is not zero:
            move_axis_steps() along right/left for |y_grid| squares
        hover for hover_seconds at the arrived location

    Args:
        drone: the connected Drone instance.
        x_grid (int): grid squares forward (positive) or backward
            (negative) to travel. 0 = no movement on this axis.
        y_grid (int): grid squares right (positive) or left
            (negative) to travel. 0 = no movement on this axis.
        speed_ms (float): speed in m/s for each 15.24 cm move.
        hover_seconds (float): how long to hover once arrived.

    Returns:
        None. Leaves the drone hovering at the target grid location.
    """
    print(f"Flying to grid location ({x_grid}, {y_grid})...")

    # X axis: forward/backward
    if x_grid != 0:
        print(f"  X axis: {abs(x_grid)} grid square(s) "
              f"{'forward' if x_grid > 0 else 'backward'}")
        move_axis_steps(drone, x_grid, drone.move_forward, drone.move_backward, speed_ms)

    # Y axis: right/left
    if y_grid != 0:
        print(f"  Y axis: {abs(y_grid)} grid square(s) "
              f"{'right' if y_grid > 0 else 'left'}")
        move_axis_steps(drone, y_grid, drone.move_right, drone.move_left, speed_ms)

    print(f"Arrived at ({x_grid}, {y_grid}). Hovering {hover_seconds}s.")
    drone.hover(hover_seconds)


def return_to_start(drone, x_grid, y_grid, speed_ms=MOVE_SPEED_MS, hover_seconds=HOVER_SECONDS):
    """
    Fly back to (0, 0) from a given grid location, by calling
    fly_to_grid() with both coordinates negated - the exact reverse
    path, same axes, opposite direction.

    Pseudocode:
        call fly_to_grid(drone, -x_grid, -y_grid)
        # this reuses the same X-then-Y movement logic, just
        # traveling the negated distance back toward (0, 0)

    Args:
        drone: the connected Drone instance.
        x_grid (int): the X grid coordinate the drone is currently
            at (not the distance to travel - the function negates it).
        y_grid (int): the Y grid coordinate the drone is currently at.
        speed_ms (float): speed in m/s for each 15.24 cm move.
        hover_seconds (float): how long to hover once back at (0, 0).

    Returns:
        None. Leaves the drone hovering at (0, 0).
    """
    print(f"Returning to start (0, 0) from ({x_grid}, {y_grid})...")
    fly_to_grid(drone, -x_grid, -y_grid, speed_ms=speed_ms, hover_seconds=hover_seconds)
    print("Back at start (0, 0).")


def main():
    """
    Entry point. Connects to the drone and runs the full mission:
    takeoff, fly to TARGET_GRID using the X-then-Y taxicab path,
    hover, return to (0, 0) via the reverse path, hover, then land.

    The flight logic runs inside a try/finally block: if anything
    raises an exception mid-flight, the finally block still calls
    drone.land() and drone.close() so the drone doesn't get left
    airborne with no landing command issued.

    Pseudocode:
        create Drone object and pair
        take off, hover 5 seconds at (0, 0)
        try:
            fly_to_grid(target_x, target_y)     # travel out, hover at target
            return_to_start(target_x, target_y)  # travel back, hover at (0,0)
        finally:
            land
            close the connection
            (runs even if an exception occurred above)
    """
    drone = Drone()
    drone.pair()

    drone.takeoff()
    print("Location (0, 0): hovering at start.")
    drone.hover(HOVER_SECONDS)

    target_x, target_y = TARGET_GRID

    try:
        fly_to_grid(drone, target_x, target_y)
        return_to_start(drone, target_x, target_y)
        print("Flight plan complete.")
    finally:
        print("Landing.")
        drone.land()
        drone.close()


if __name__ == "__main__":
    main()
