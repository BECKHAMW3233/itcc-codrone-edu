# Python Concepts Used in This Repo

This is a plain-language explainer for the Python patterns that show
up repeatedly in `missions/` and `scripts/`. It does **not** assume
you've taken a full programming course — CTI-110 (IT Foundations) or
similar is plenty, even though that course only touches programming
as one topic among several (AI, databases, web dev). If you already
know what variables, if statements, and loops are, skip ahead to
section 1. If any of that is still new, section 0 covers it first.
Each mission script links back to this doc instead of re-explaining
these ideas every time.

If a concept below still doesn't make sense after reading it, ask in
the club — that's normal, not a sign you're behind. These are things
that take a few real examples to click.

---

## 0. If you've never written any code before

Everything from section 1 onward assumes you know what a **variable**,
an **if statement**, and a **loop** are. Here's the fast version:

- A **variable** is a named box that holds a value.
  `altitude = 50` creates a variable called `altitude` holding the
  number `50` — you can use `altitude` later in the code instead of
  retyping `50` everywhere.
- An **if statement** runs a piece of code only when something is
  true. `if altitude > 100: land()` means "only call `land()` if
  `altitude` is actually bigger than 100 at that point in the code."
- A **loop** repeats the same code multiple times instead of you
  typing it out over and over by hand — section 5 below covers the
  specific kind used in this repo.

If none of that clicked yet, that's completely normal — CTI-110 is a
broad IT survey course, not a hands-on programming class, so this may
be close to your first real exposure to any of it. A free 30-60
minute walkthrough like
[Python's official beginner's guide](https://www.python.org/about/gettingstarted/)
will make the rest of this document click faster. Otherwise, keep
reading — section 9 at the end still gives you a concrete, step-by-step
plan for approaching a real script even while some of this still feels new.

## 1. What a function actually is

You've probably used functions already, even if you didn't think
about it that way — `print("hello")` is a function call. A function
is just a named, reusable block of code that can take some
information in (called **arguments** or **parameters**) and
optionally hand some information back out (called the **return
value**).

```python
def add_five(number):
    return number + 5

result = add_five(10)   # result is now 15
```

- `def add_five(number):` — this line **defines** the function. It
  doesn't run anything yet — it just teaches Python "here's a recipe
  called `add_five` that needs one ingredient called `number`."
- `add_five(10)` — this line **calls** the function, actually running
  it with `10` plugged in for `number`.
- `return number + 5` — this hands the result back to whatever called
  the function, so it can be stored in a variable (`result`) or used
  right away.

In the mission scripts, you'll see functions like:

```python
def climb_to(drone, target_cm):
    ...
```

This defines a function named `climb_to` that needs two pieces of
information to run: `drone` (the connected drone object) and
`target_cm` (how high to climb, in centimeters). Further down in the
script, you'll see it actually being used:

```python
climb_to(drone, 91.44)
```

This is the **call** — it actually runs the `climb_to` function,
plugging in the real drone connection and the number `91.44`.

**Why the scripts are broken into functions instead of one long
block of code:** it makes each piece reusable and testable on its
own, and it makes the overall flow (see `main()` below) read almost
like an outline of the mission, instead of one giant wall of code.

## 2. Reading a function's documentation (docstring)

Every function in these scripts starts with a triple-quoted string
right after the `def` line — that's called a **docstring**, and it's
not code that runs, it's documentation:

```python
def climb_to(drone, target_cm):
    """
    Climb from the drone's current altitude to a target altitude.

    Args:
        drone: the connected Drone instance.
        target_cm (float): target altitude in cm.

    Returns:
        None.
    """
    ...
```

- **Args:** section — lists every piece of information the function
  needs, and what each one means.
- **Returns:** section — tells you what, if anything, comes back out
  of the function. `None` means "nothing — this function does
  something (like moving the drone) but doesn't hand back a value to
  use."

If you're trying to understand what a function does, read its
docstring before reading its actual code — it should tell you the
"what" and "why" so you don't have to reverse-engineer it from the
logic.

## 3. `main()` — the starting point of every script

Every mission script has a function called `main()`, and at the very
bottom of the file:

```python
if __name__ == "__main__":
    main()
```

Don't worry about exactly what `if __name__ == "__main__":` means
line-by-line yet — for now, just know that this is the standard
Python way of saying **"when this file is run directly, start by
calling `main()`."** `main()` is where you should start reading any
script in this repo — it's written to read almost like a summary of
the whole mission, calling the other functions in order.

## 4. Tuples — grouping related values together

A **tuple** is a fixed group of values bundled together with
parentheses, like a small, unchangeable list:

```python
point = (10, 20, 30)
```

This creates one variable, `point`, that actually holds three values
at once. You'll see this a lot in `waypoint_route.py`, where each
waypoint is a tuple of five values:

```python
(100, 0, 80, 0, "Waypoint 1: 100cm forward, 80cm altitude, facing forward")
```

That's one waypoint, bundling together an X position, Y position, Z
position, a heading, and a text label — all as one unit, so they stay
grouped together instead of being five separate, disconnected
variables.

### Unpacking a tuple

You'll also see code like this:

```python
for x_cm, y_cm, z_cm, heading, label in waypoints:
    ...
```

This is looping over a list of tuples (`waypoints`), and on each pass
through the loop, it **unpacks** one tuple into five separate
variable names (`x_cm`, `y_cm`, `z_cm`, `heading`, `label`) — matched
up in order. It's shorthand for grabbing all five pieces out of the
tuple at once instead of writing `waypoint[0]`, `waypoint[1]`, etc.

## 5. Loops over lists of things

A `for` loop in these scripts almost always means "do this same
action once for each item in a list." For example:

```python
for step_cm in altitude_steps_cm:
    climb_to(drone, step_cm)
```

This means: for every altitude value in the `altitude_steps_cm` list
(e.g. 15.24, 30.48, 45.72, ...), run `climb_to()` once with that
value. The loop handles repeating the climb for every step so the
script doesn't need one line of code per altitude step written out
by hand.

## 6. Default argument values

You'll see function definitions like this:

```python
def fly_to_waypoint(drone, x_cm, y_cm, z_cm, heading, label,
                     velocity_ms=0.5, hover_seconds=5):
    ...
```

`velocity_ms=0.5` and `hover_seconds=5` are **default values** — if
whoever calls this function doesn't specify a value for those two,
Python automatically uses `0.5` and `5`. This lets you call the
function with just the required information most of the time:

```python
fly_to_waypoint(drone, 100, 0, 80, 0, "example")
```

...and it'll automatically use the default speed and hover time,
without you having to type them out every single call. But you can
still override them if needed:

```python
fly_to_waypoint(drone, 100, 0, 80, 0, "example", velocity_ms=1.0)
```

## 7. `try` / `finally` — making sure the drone always lands

Every mission script wraps its flight logic like this:

```python
try:
    # ... fly the mission ...
finally:
    drone.land()
    drone.close()
```

**The problem this solves:** if something goes wrong partway through
a flight — a sensor gives a weird reading, the code hits a bug, the
connection drops — normally Python would just stop running the
script right there, mid-air, with the drone still flying and no
landing command ever sent.

**What `try`/`finally` does about it:** everything inside the `try:`
block runs as normal. But no matter what happens inside that block —
whether it finishes successfully or hits an error partway through —
the code inside `finally:` is **guaranteed to run anyway**. So
`drone.land()` and `drone.close()` always get called, even if the
mission crashes halfway through, which means the drone doesn't get
left flying with no way to bring it down automatically.

This is a safety pattern, not just a style choice — it's one of the
more important things to understand in these scripts, since it's
directly about not leaving a drone stranded in the air.

## 8. Comments (`#`) vs. docstrings (`"""..."""`)

You'll see two kinds of non-code text in these files:

- **Comments** start with `#` and explain a single line or a small
  chunk of code right where they appear:
  ```python
  drone.set_throttle(40)   # throttle up to start climbing
  ```
- **Docstrings** are the triple-quoted `"""..."""` blocks at the top
  of a file or right after a `def` line — they document an entire
  file or function's purpose, not just one line (see section 2
  above).

Neither one is code that actually runs — they're both just notes for
humans reading the file.

## 9. Reading a mission script for the first time — suggested order

1. Read the big docstring at the very top of the file — it explains
   what the mission does and why, in plain English, plus pseudocode
   for the whole flow.
2. Find `main()` near the bottom and read it — it should read like an
   outline of the mission, calling the other functions in the order
   they happen.
3. For each function `main()` calls, jump to that function's own
   definition and read its docstring.
4. Only then read the actual code line-by-line inside each function,
   now that you know what it's supposed to accomplish.

Trying to read a file top-to-bottom, function-body-first, is usually
harder than starting from `main()` and working outward — treat
`main()` as the table of contents for the whole script.
