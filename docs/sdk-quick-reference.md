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

## Power-based movement (simpler, less precise)

```python
drone.go("forward", 30, 1)   # direction, power %, duration in seconds
drone.go("backward", 30, 1)
drone.go("left", 30, 1)
drone.go("right", 30, 1)
```

## Altitude / throttle

There is no single "fly to absolute altitude" call. To climb or
descend to a target height, use `set_throttle()` combined with
`move()` while polling `get_height()`:

```python
drone.set_throttle(40)
while drone.get_height("cm") < target_cm:
    drone.move()
drone.set_throttle(0)
drone.move()
```

## Sensors

```python
drone.get_height(unit="cm")        # height above ground/takeoff
drone.get_front_range(unit="cm")   # distance to object in front (0-150cm)
drone.get_bottom_range(unit="cm")  # distance to surface below
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
drone.turn(degrees)   # positive/negative for CW/CCW - check current SDK docs for sign convention
```

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
