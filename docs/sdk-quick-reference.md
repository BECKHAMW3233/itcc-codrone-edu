# CoDrone EDU Python SDK - Quick Reference

Verified against the official Robolink documentation
(docs.robolink.com/docs/CoDroneEDU/Python/) and Robolink's own example
scripts. This is a starting cheat sheet, not the full API — see the
official docs for anything not covered here.

## Setup

```python
from codrone_edu.drone import *

drone = Drone()
drone.pair()
```

## Takeoff / landing

```python
drone.takeoff()
drone.land()
drone.close()          # always call at the end of your script
drone.emergency_stop()  # immediate motor cutoff - use with care
```

## Hovering

```python
drone.hover(seconds)   # hover for a set duration
drone.hover()           # hover indefinitely until another command
```

## Precise distance movement (optical flow sensor)

```python
drone.move_forward(distance, units="cm", speed=1)
drone.move_backward(distance, units="cm", speed=1)
drone.move_left(distance, units="cm", speed=1)
drone.move_right(distance, units="cm", speed=1)
```

- `units`: `"cm"`, `"in"`, `"ft"`, or `"m"`
- `speed`: meters per second, default 1.0, max 2.0
- Needs a well-lit, patterned surface underneath for accuracy
- Each call is single-axis only - moving diagonally or changing
  altitude while moving requires `move_distance()` or
  `send_absolute_position()` below instead.

## Multi-axis movement (relative, simultaneous X/Y/Z)

```python
drone.move_distance(x, y, z, velocity)
```

- All distances in **meters** (not cm) and relative to the drone's
  CURRENT position and heading.
- Moves all three axes simultaneously - e.g.
  `drone.move_distance(0.5, 0.5, 0.25, 1)` moves forward 0.5m, left
  0.5m, and up 0.25m all at once, at 1 m/s.
- `velocity` is in meters/second.
- **Important:** this is relative to the drone's CURRENT heading, not
  the world/takeoff frame. If the drone has turned since takeoff,
  "forward" here means forward from its current facing direction, not
  from its original launch orientation. This makes `move_distance()`
  risky to use after a turn unless you're deliberately building
  heading-relative movement - for absolute/world-frame movement, use
  `send_absolute_position()` instead.

## Absolute position + heading (world-frame waypoints)

```python
drone.send_absolute_position(positionX, positionY, positionZ, velocity, heading, rotationalVelocity)
```

- `positionX`, `positionY`, `positionZ`: **meters**, absolute position
  measured from the drone's first takeoff location (not relative to
  current position). Range: -10m to 10m on X/Y.
- `velocity`: meters/second for the move.
- `heading`: absolute target heading in degrees (the z-angle the
  drone should be facing once it arrives).
- `rotationalVelocity`: degrees/second for the turn (0-360).
- Unlike `move_distance()`, this is **world-frame** - coordinates
  always mean the same physical spot regardless of the drone's
  current heading, which makes it the safer choice for a sequence of
  waypoints that includes turns.
- Needs a well-lit, patterned surface for the optical flow sensor to
  track position accurately.

```python
# Example: fly a 0.5m square while ending each leg facing a new heading
drone.send_absolute_position(0.5, 0,   0.8, 0.5, 90,  90)
drone.send_absolute_position(0.5, 0.5, 0.8, 0.5, 180, 90)
drone.send_absolute_position(0,   0.5, 0.8, 0.5, 270, 90)
drone.send_absolute_position(0,   0,   0.8, 0.5, 0,   90)
```

## Power-based movement (simpler, less precise)

```python
drone.go("forward", 30, 1)   # direction, power %, duration in seconds
drone.go("backward", 30, 1)
drone.go("left", 30, 1)
drone.go("right", 30, 1)
```

## Altitude / throttle

There is no single "fly to absolute altitude" call using throttle
alone. To climb or descend to a target height using throttle, use
`set_throttle()` combined with `move()` while polling `get_height()`:

```python
drone.set_throttle(40)
while drone.get_height("cm") < target_cm:
    drone.move()
drone.set_throttle(0)
drone.move()
```

For a specific target altitude combined with horizontal movement and
heading in one command, prefer `send_absolute_position()` above
instead of manual throttle control - it handles altitude (Z) as part
of the same absolute-position command.

## Sensors

```python
drone.get_height(unit="cm")        # height above ground/takeoff
drone.get_front_range(unit="cm")   # distance to object in front (0-150cm)
drone.get_bottom_range(unit="cm")  # distance to surface below
drone.get_pos_x() / get_pos_y() / get_pos_z()   # position from takeoff, meters
drone.get_position_data()          # full position data list
```

- `get_front_range()` returns `999` when out of range or timed out,
  and `-10` or `0` on a sensor error.
- `get_bottom_range()`/`get_height()` return `0` when the drone is
  sitting on a surface (the sensor shuts off so the color sensor can
  work).

## Obstacle helpers

```python
drone.avoid_wall(timeout=2, distance=50)   # fly forward until distance to wall reached
drone.keep_distance(timeout=2, distance=50) # maintain a set distance from an object
```

## Rotation

```python
drone.turn_left(degrees)     # turn left by a relative amount
drone.turn_right(degrees)    # turn right by a relative amount
drone.turn_degree(degrees)   # turn to an absolute heading
```

- `turn_left()`/`turn_right()` support rotations above 180 degrees
  (up to 360).
- For a waypoint sequence, `send_absolute_position()`'s built-in
  `heading` parameter is usually simpler than calling these
  separately - it turns and moves in one command.

## Notes for mission scripts

- Always end with `drone.land()` then `drone.close()`.
- Wrap flights in `try`/`finally` if you want to guarantee landing
  even if something errors mid-script:

```python
drone = Drone()
drone.pair()
try:
    drone.takeoff()
    # ... mission logic ...
finally:
    drone.land()
    drone.close()
```

- Full official docs: https://docs.robolink.com/docs/CoDroneEDU/Python/
