"""
CoDrone EDU - Staged Altitude Climb with Square Pattern at 3 ft
------------------------------------------------------------------
Behavior:
  1. Take off.
  2. Climb in 6-inch increments: 6, 12, 18, 24, 30, 36, 42, 48, 54, 60 in
     (60 in = 5 ft). Hover for 5 seconds at each altitude step.
  3. When altitude reaches 36 in (3 ft):
       - Hover 5s at start point (location 0)
       - Move to location 1 (left 12in)   -> hover 5s
       - Move to location 2 (forward 12in) -> hover 5s
       - Move to location 3 (right 12in)   -> hover 5s
       - Move back to location 0 (backward 12in) -> hover 5s
     The movement itself does not count toward hover time - each hover
     only starts once the drone has stopped at that location.
  4. Resume the 6-inch climb steps until reaching 5 ft.
  5. Land.

Notes:
  - move_forward/backward/left/right() use the optical flow sensor for
    precise distance. Fly over a well-lit, patterned surface for best
    accuracy.
  - Altitude is climbed using set_throttle() + move() while monitoring
    get_height(), since there is no single "fly to absolute altitude"
    call in the SDK.
  - Adjust HOVER_SECONDS, CLIMB_THROTTLE, and SQUARE_SIDE_IN as needed.
"""

from codrone_edu.drone import *
import time

# ---------------- Configuration ----------------
INCH_TO_CM = 2.54

STEP_IN = 6                 # altitude increment, inches
TARGET_FT = 5                # final altitude, feet
SQUARE_AT_FT = 3             # altitude (feet) at which to fly the square
SQUARE_SIDE_IN = 12          # square side length, inches

HOVER_SECONDS = 5            # hover time at each altitude step and at each square location
CLIMB_THROTTLE = 40          # throttle % used to climb between steps
CLIMB_TOLERANCE_CM = 3       # how close (cm) to target before stopping climb
MOVE_SPEED_MS = 0.5          # speed (m/s) for the square-pattern moves

# Build the list of altitude steps in inches: 6, 12, 18, ... up to 60 (5 ft)
target_in = TARGET_FT * 12
altitude_steps_in = list(range(STEP_IN, target_in + 1, STEP_IN))
square_at_in = SQUARE_AT_FT * 12


def climb_to(drone, target_in):
    """Climb from current altitude to target_in (inches) using throttle,
    checking height with get_height() until within tolerance."""
    target_cm = target_in * INCH_TO_CM
    current_cm = drone.get_height("cm")

    drone.set_throttle(CLIMB_THROTTLE)
    while current_cm < target_cm - CLIMB_TOLERANCE_CM:
        drone.move()
        current_cm = drone.get_height("cm")
        time.sleep(0.05)

    # Stop climbing, reset throttle, hover in place
    drone.set_throttle(0)
    drone.move()
    drone.hover(HOVER_SECONDS)


def fly_square(drone, side_in, speed, hover_seconds):
    """Fly a square: hover at start, then move+hover at each of the 4
    corners (left, forward, right, backward), returning to the start
    point. Movement time does not count as hover time - each hover
    begins only after the drone has stopped at that location."""
    # Location 0: starting point
    print("  Location 0 (start): hovering...")
    drone.hover(hover_seconds)

    # Location 1: left
    drone.move_left(side_in, units="in", speed=speed)
    print("  Location 1 (left): hovering...")
    drone.hover(hover_seconds)

    # Location 2: forward
    drone.move_forward(side_in, units="in", speed=speed)
    print("  Location 2 (forward): hovering...")
    drone.hover(hover_seconds)

    # Location 3: right
    drone.move_right(side_in, units="in", speed=speed)
    print("  Location 3 (right): hovering...")
    drone.hover(hover_seconds)

    # Back to location 0: backward, returning to start
    drone.move_backward(side_in, units="in", speed=speed)
    print("  Back at location 0: hovering...")
    drone.hover(hover_seconds)


def main():
    drone = Drone()
    drone.pair()

    drone.takeoff()
    drone.hover(HOVER_SECONDS)

    for step_in in altitude_steps_in:
        print(f"Climbing to {step_in} in ({step_in / 12:.2f} ft)...")
        climb_to(drone, step_in)
        current_ft = drone.get_height("cm") / INCH_TO_CM / 12
        print(f"  Now at approx {current_ft:.2f} ft. Hovering {HOVER_SECONDS}s.")

        # At 3 ft, fly the square pattern before continuing to climb
        if step_in == square_at_in:
            print("Reached 3 ft - flying square pattern (left, forward, right, backward)...")
            fly_square(drone, SQUARE_SIDE_IN, MOVE_SPEED_MS, HOVER_SECONDS)
            print("Square complete. Still at 3 ft. Resuming climb...")

    print("Reached final altitude (5 ft). Landing.")
    drone.land()
    drone.close()


if __name__ == "__main__":
    main()
