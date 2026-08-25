# Contributing to the ITCC CoDrone EDU Project

This project is a shared space for ITCC members to design and submit
their own CoDrone EDU flight missions. Follow these guidelines so
everyone's code is easy to read, run, and build on.

**New to Git, GitHub, or Python?** This guide assumes you can already
clone the repo, create a branch, and open a pull request — if any of
that isn't familiar yet, read
[`docs/getting-access-and-setup.md`](docs/getting-access-and-setup.md)
first, it walks through all of it step by step (including what a
terminal even is). If typing Git commands isn't something you want to
learn right now, [`docs/using-claude-code.md`](docs/using-claude-code.md)
covers doing all of this — branching, committing, opening the pull
request — by describing what you want in plain English instead. If a
term like "docstring" below is new, see
[`docs/python-concepts-guide.md`](docs/python-concepts-guide.md) — it
covers the Python patterns used across this repo in plain language,
starting from the absolute basics if needed.

## Before you start

1. Make sure you have `codrone-edu` installed and can run the example
   mission in `missions/altitude_square_demo.py` successfully.
2. Plan your flight path on paper first: takeoff point, altitude
   changes, movement pattern, any tasks (sensor readings, hovering at
   specific points, landing at a separate location, return flight),
   and the final landing point. Sketch it out before writing code.
3. Know your hardware limits: max ~8 minutes flight time per battery,
   indoor use only unless otherwise cleared, and keep movements within
   a space you've checked for obstacles.

## Submitting a mission

1. **Create a branch** named after your mission, e.g.
   `yourname-perimeter-scan` or `yourname-figure-eight`. This repo
   uses direct branches, not forks — you don't need your own copy of
   the repo, just your own branch inside this one (see
   `docs/getting-access-and-setup.md` if branches are a new concept).
2. **Add your script to `missions/`** with a clear, descriptive
   filename (e.g. `perimeter_scan_jdoe.py`, not `test1.py` or
   `drone_script.py`).
3. **Include a header docstring** at the top of your script that
   describes:
   - What the mission does, step by step
   - Starting assumptions (takeoff point, orientation, altitude)
   - Any hardcoded distances/heights/speeds and why you chose them
   - Whether it lands at the takeoff point or a different location
4. **Use configuration variables**, not magic numbers, wherever
   reasonable — see `altitude_square_demo.py` for the pattern (e.g.
   `HOVER_SECONDS`, `STEP_CM` defined near the top, not buried in
   function calls). ("Magic number" means a value typed directly into
   your code with no explanation, like `time.sleep(5)` — a reader has
   no way to know why it's 5, or whether that same 5 matters
   elsewhere. A named variable like `HOVER_SECONDS = 5` at the top of
   the file fixes that.)
5. **Test incrementally.** Get takeoff/land working first, then add
   one movement at a time. Don't write the whole mission blind and
   test it all at once.
6. **Open a pull request** with:
   - A short description of the mission (what it does and why)
   - Any known limitations or things you weren't able to test
   - Confirmation that you test-flew it (or a note if you couldn't)

## Code style

- Keep each mission as a single, runnable script — someone should be
  able to `python missions/your_script.py` and have it work with no
  extra setup beyond pairing the drone.
- Use descriptive variable and function names (`fly_perimeter()`, not
  `f1()`).
- Comment your flight logic, especially anything involving sensor
  polling, loops, or conditional branches — the *why*, not just the
  *what*.
- If your mission reuses logic another member already wrote (e.g. a
  climb-to-altitude helper), consider moving that helper into
  `scripts/` instead of copy-pasting it, and note that in your PR.

## Reviewing others' missions

Any club member can review a pull request. When reviewing, check for:

- Does the docstring clearly describe the flight path?
- Are altitude/distance/speed values reasonable for our flying space?
- Is there a clear `drone.land()` (and `drone.close()`) at the end of
  every code path, including error cases?
- Would you feel comfortable running this without watching the code
  execute line by line?

## Safety reminders for every submission

- No mission should assume an unlimited or unbounded flight area —
  state the space you tested it in.
- Every mission must land the drone by the end of the script (or
  clearly document that it's an intentionally partial/test script).
- If a mission includes a return-to-start or return-to-launch step,
  test that specific piece separately before combining it with the
  full mission.
