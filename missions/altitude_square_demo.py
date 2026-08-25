"""
CoDrone EDU - Staged Altitude Climb with Square Pattern at 91.44 cm
==================================================================

STATUS: UNTESTED ON HARDWARE. This script has been written against
the documented CoDrone EDU Python SDK but has not yet been flown.
Test it in a clear, obstacle-free space at low throttle before
relying on it, and be ready to hit drone.land() / drone.emergency_stop()
manually (e.g. from the controller) if it behaves unexpectedly.

WHAT THIS MISSION DOES
-----------------------
Takes off, climbs to 152.4 cm in 15.24 cm steps (hovering 5 seconds
at each step), and when it passes through 91.44 cm, pauses the climb
to fly a 30.48 x 30.48 cm square pattern before continuing upward.

(These cm values correspond to a flight plan originally specified in
feet/inches: climb to 5 ft in 6 in steps, with a 12x12 in square flown
at the 3 ft mark. All units here are cm to match the SDK natively -
see UNIT NOTES below.)

COORDINATE / UNIT NOTES
-------------------------
  - ALL distances and speeds in this script are in centimeters (cm)
    and centimeters/second, matching the units the CoDrone EDU SDK
    natively accepts - no unit conversion happens anywhere in this
    file.
  - There is no absolute "fly to altitude X" command in the SDK, so
    altitude is climbed manually: throttle up, poll get_height("cm"),
    stop throttle once within tolerance of the target.

PSEUDOCODE
-----------
    connect to drone
    take off
    hover 5 seconds

    for each altitude step in [15.24, 30.48, 45.72, 60.96, 76.2,
                                 91.44, 106.68, 121.92, 137.16, 152.4] cm:
        climb from current altitude to this step's altitude
            (set throttle up, loop: move() + check get_height("cm"),
             stop when within tolerance of target)
        hover 5 seconds

        if this step is 91.44 cm:
            # fly a 30.48 x 30.48 cm square, hovering 5s at each corner
            hover 5 seconds                      # location 0 (start)
            move left 30.48 cm
            hover 5 seconds                      # location 1
            move forward 30.48 cm
            hover 5 seconds                      # location 2
            move right 30.48 cm
            hover 5 seconds                      # location 3
            move backward 30.48 cm                # back to location 0
            hover 5 seconds                      # location 0 (returned)
            # climb resumes on the next loop iteration

    land
    close connection

KNOWN LIMITATIONS
-------------------
  - No bounds checking - nothing stops CLIMB_THROTTLE or TARGET_CM
    from being set to unsafe values for the room you're flying in.
  - move_forward/backward/left/right() rely on the optical flow
    sensor for precise distance. Fly over a well-lit, patterned
    surface for best accuracy; results may drift on plain/reflective
    floors.
  - Adjust HOVER_SECONDS, CLIMB_THROTTLE, and SQUARE_SIDE_CM in the
    configuration section below as needed for your space and drone.
  - Movement speed is configured in cm/second (MOVE_SPEED_CM_PER_SEC),
    converted to meters/second only at the point of the actual SDK
    call, since the SDK's speed parameter is in m/s. Max SDK speed is
    2.0 m/s (200 cm/sec) - values above that will likely be clamped
    or rejected by the drone firmware.

NEW TO PYTHON? READ THIS FIRST
---------------------------------
If terms like "function," "docstring," "tuple," or "try/finally"
below aren't familiar yet, see
docs/python-concepts-guide.md in this repo before reading the rest of
this file - it explains those ideas in plain language with small
examples, and this script will make a lot more sense afterward. The
short version: start reading at main() near the bottom of this file -
it lists out the mission step by step - then look up each function
main() calls, one at a time.
"""

from codrone_edu.drone import *
import time

# ---------------- Configuration ----------------
STEP_CM = 15.24              # altitude increment, cm (= 6 inches)
TARGET_CM = 152.4            # final altitude, cm (= 5 feet)
SQUARE_AT_CM = 91.44         # altitude (cm) at which to fly the square (= 3 feet)
SQUARE_SIDE_CM = 30.48       # square side length, cm (= 12 inches)

HOVER_SECONDS = 5            # hover time at each altitude step and at each square location
CLIMB_THROTTLE = 40          # throttle % used to climb between steps
CLIMB_TOLERANCE_CM = 3       # how close (cm) to target before stopping climb

# Movement speed for the square-pattern moves, in cm/second. The
# SDK's move_forward/backward/left/right() functions take speed in
# meters/second (max 2.0 m/s = 200 cm/sec) - converted at the call site.
MOVE_SPEED_CM_PER_SEC = 50    # cm per second
MOVE_SPEED_MS = MOVE_SPEED_CM_PER_SEC / 100   # cm/sec -> m/s

# Build the list of altitude steps in cm: 15.24, 30.48, ... up to 152.4 (5 ft)
_num_steps = round(TARGET_CM / STEP_CM)
altitude_steps_cm = [round(STEP_CM * n, 2) for n in range(1, _num_steps + 1)]


def climb_to(drone, target_cm):
    """
    Climb from the drone's current altitude to a target altitude.

    IN PLAIN LANGUAGE: there's no built-in "fly up to exactly this
    height" command in the drone's library. Instead, this function
    turns the upward power (throttle) on, keeps checking the current
    height sensor in a loop, and turns the throttle back off once the
    drone is close enough to the target. Think of it like holding
    down a bicycle pedal and checking your speedometer over and over
    until you hit the speed you want, then letting go of the pedal.

    Pseudocode:
        read current height with get_height("cm")
        set throttle to CLIMB_THROTTLE (positive = climb)
        while current height < target - tolerance:
            call move() to apply the current throttle for one tick
            re-read current height
            small sleep to avoid hammering the sensor/radio link
        set throttle back to 0 and call move() once to apply it
        hover in place for HOVER_SECONDS

    Args (the information this function needs to run):
        drone: the connected Drone instance.
        target_cm (float): target altitude in cm, measured from the
            takeoff point (i.e. what get_height("cm") returns at 0
            throttle when sitting on the ground before takeoff).

    Returns (what comes back out of this function):
        None - meaning this function doesn't hand back a value, it
        just does something (climbs the drone) and leaves it hovering
        at approximately target_cm (within CLIMB_TOLERANCE_CM).
    """
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


def fly_square(drone, side_cm, speed_ms, hover_seconds):
    """
    Fly a 4-sided square pattern, hovering at every corner including
    the return to the starting point.

    IN PLAIN LANGUAGE: this just calls four movement commands in a
    row - left, forward, right, backward - with a pause (hover)
    after each one. Because each side is the same length and each
    turn is 90 degrees, the drone traces a square shape and ends up
    back where it started.

    Pseudocode:
        hover at location 0 (current position, the start point)
        move left side_cm      -> now at location 1
        hover at location 1
        move forward side_cm   -> now at location 2
        hover at location 2
        move right side_cm     -> now at location 3
        hover at location 3
        move backward side_cm  -> back at location 0
        hover at location 0 (confirms the drone returned to start)

    Movement time is never counted as hover time - each hover call
    only begins once the preceding move has fully completed, so the
    printed "location" hovers reflect time spent stationary only.

    Args (the information this function needs to run):
        drone: the connected Drone instance.
        side_cm (float): length of each side of the square, in cm.
        speed_ms (float): speed in m/s for each horizontal move
            (already converted from cm/sec at the configuration level).
        hover_seconds (float): how long to hover at each of the 4
            corners (including the return to location 0).

    Returns (what comes back out of this function):
        None - this function doesn't hand back a value, it just flies
        the square and leaves the drone hovering back at its starting
        horizontal position, at whatever altitude it was already at.
    """
    # Location 0: starting point
    print("  Location 0 (start): hovering...")
    drone.hover(hover_seconds)

    # Location 1: left
    drone.move_left(side_cm, units="cm", speed=speed_ms)
    print("  Location 1 (left): hovering...")
    drone.hover(hover_seconds)

    # Location 2: forward
    drone.move_forward(side_cm, units="cm", speed=speed_ms)
    print("  Location 2 (forward): hovering...")
    drone.hover(hover_seconds)

    # Location 3: right
    drone.move_right(side_cm, units="cm", speed=speed_ms)
    print("  Location 3 (right): hovering...")
    drone.hover(hover_seconds)

    # Back to location 0: backward, returning to start
    drone.move_backward(side_cm, units="cm", speed=speed_ms)
    print("  Back at location 0: hovering...")
    drone.hover(hover_seconds)


def main():
    """
    Entry point. Connects to the drone and runs the full mission:
    takeoff, staged 15.24 cm altitude climb to 152.4 cm with a
    5-second hover at every step, a 30.48x30.48 cm square pattern
    flown at the 91.44 cm step, then landing.

    The flight logic runs inside a try/finally block: if anything
    raises an exception mid-flight (a sensor error, a dropped
    connection, etc.), the finally block still calls drone.land()
    and drone.close() so the drone doesn't get left airborne with no
    landing command issued.

    Pseudocode:
        create Drone object and pair
        take off, hover 5 seconds
        try:
            for each altitude step from 15.24cm up to 152.4cm, by 15.24cm:
                climb to this step, hover 5 seconds
                if this step is 91.44cm:
                    fly the square pattern (see fly_square())
        finally:
            land
            close the connection
            (runs even if an exception occurred above)
    """
    drone = Drone()
    drone.pair()

    drone.takeoff()
    drone.hover(HOVER_SECONDS)

    try:
        for step_cm in altitude_steps_cm:
            print(f"Climbing to {step_cm} cm...")
            climb_to(drone, step_cm)
            current_cm = drone.get_height("cm")
            print(f"  Now at approx {current_cm:.2f} cm. Hovering {HOVER_SECONDS}s.")

            # At 91.44 cm (3 ft), fly the square pattern before continuing to climb
            if abs(step_cm - SQUARE_AT_CM) < 0.01:
                print("Reached 91.44 cm - flying square pattern (left, forward, right, backward)...")
                fly_square(drone, SQUARE_SIDE_CM, MOVE_SPEED_MS, HOVER_SECONDS)
                print("Square complete. Still at 91.44 cm. Resuming climb...")

        print("Reached final altitude (152.4 cm).")
    finally:
        print("Landing.")
        drone.land()
        drone.close()


if __name__ == "__main__":
    main()
