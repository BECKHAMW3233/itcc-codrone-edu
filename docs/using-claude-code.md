# Using Claude Code With This Repo (or Any Repo)

This is an optional guide for club members who want to try **Claude
Code** — an AI coding assistant — to help write, edit, and manage this
repo (or any other GitHub repo) on their own computer. You don't need
this to contribute to the project; it's just a tool some members may
find useful. This guide assumes you have **never opened Claude Code
before** and walks through it from the very first screen.

**If you've never used Git, GitHub, or a command line before, this is
probably the easier starting point.** `getting-access-and-setup.md`
teaches the real Git commands (worth learning eventually), but
everything in that guide — cloning the repo, creating a branch,
committing, pushing, opening a pull request — can also be done here by
just describing what you want in plain English. You can always learn
the underlying commands later; you don't need them to get started.

If you're new to Python or Git/GitHub themselves (separate from
Claude Code), read
[`python-concepts-guide.md`](python-concepts-guide.md) and
[`getting-access-and-setup.md`](getting-access-and-setup.md) first —
this guide assumes you already know what a file, a folder, and typing
into an app are, and it builds on the Git workflow described there.

---

## What Claude Code actually is

Claude Code is a program you talk to like a chat app — you type a
message in plain English, it types back — except it's also connected
to a real folder of files on your computer. Unlike a normal chatbot,
it can actually **open, search, and edit those files, and run
commands** (like `python` or `git`) in that folder on your behalf. You
ask for something ("fix the bug in `converter.py`," "clone this
repo"), and it does the work itself, showing you what it changed as
it goes — rather than just describing what you should type.

## Opening it for the first time

Claude Code shows up in a few different places depending on what your
club/school has set up for you — you likely only have access to one
of these, and any one of them works the same way underneath:

- **Claude Desktop app** — a regular app window (Mac or Windows) with
  a place to type, like any chat app.
- **A terminal window** — a plain black/white text window where you
  type a command to start it.
- **claude.ai/code** — a website version, used in a browser.
- **A code editor extension** (e.g. inside VS Code) — a side panel
  that opens next to your files.

Whichever one you have, the very first thing that matters is:
**Claude Code needs to be pointed at the right folder** — in this
case, the folder where you cloned this repo (see
`getting-access-and-setup.md` if you haven't done that yet). If it
opens in the wrong folder, it won't see this repo's files at all.

- In the **desktop app** or a **terminal**, this usually means opening
  it *from* that folder, or choosing/opening that folder as the
  project once it's running — look for an "Open Folder" option or
  similar.
- If you're using a **terminal**, this means navigating into the
  repo's folder first (e.g. `cd path/to/itcc-codrone-edu`) before
  starting it.

If any of this doesn't match what you see on your screen, that's
normal — interfaces change over time and vary by platform. Ask a club
member who's set it up before, or see the official quickstart at
https://docs.claude.com/en/docs/claude-code/quickstart.

## Having your first conversation

Once it's open and pointed at this repo's folder, there's a box to
type into, the same as any messaging app. Try something low-risk
first, just to see how it responds:

```
What does the missions folder in this repo contain?
```

Claude Code will read the actual files in `missions/` and answer based
on what's really there — not a guess. This is worth doing first
because it shows you the basic loop with zero risk: **you type a
request in plain English → it reads/checks real files → it replies
with an answer or shows you a proposed change.** Everything else in
this guide is a variation of that same loop.

## How it decides what it's allowed to do

The one thing to understand before asking it to do anything more than
answer questions: Claude Code **pauses and asks before doing anything
risky or hard to undo.** Concretely, this looks like a message on
screen describing the exact action it wants to take (e.g. "run `git
push`") with a way to approve or deny it — a button, or a yes/no
prompt, depending on which version you're using. Nothing risky happens
silently in the background; you always see it coming first.

- **Usually just happens, no asking:** reading files, searching the
  repo, editing files in your project, running checks like
  `python -m py_compile`, or read-only Git commands like `git status`
  or `git log`.
- **Always asks first:** pushing to GitHub, committing (in most
  setups), opening a pull request, or anything that would throw away
  unsaved work (like `git reset --hard`). It shows you exactly what
  it's about to do and waits for your answer before doing it.
- **Won't do at all:** type your GitHub password or a personal access
  token in for you, or push straight to `main` — GitHub's branch
  protection blocks that for every contributor, human or not, per
  `getting-access-and-setup.md`.

If you ever see it about to do something you don't want, just say no
(or click deny) — it stops and asks what you'd rather it do instead.

---

## Cloning, pulling, and pushing this repo

Once you're comfortable with the basic loop above, you can ask for
Git actions in plain English and it will run the real `git` commands,
showing you the output each time:

- *"Clone `https://github.com/BECKHAMW3233/itcc-codrone-edu` into a
  new folder"* → runs `git clone ...`
- *"Pull the latest changes from `main`"* → runs `git checkout main`
  then `git pull`
- *"Create a branch called `yourname-perimeter-scan`"* → runs
  `git checkout -b yourname-perimeter-scan`, matching the branch
  naming convention in `CONTRIBUTING.md`
- *"Commit these changes and push the branch"* → shows you the change
  and a proposed commit message, waits for you to approve, then pushes

## Editing Python files in `missions/` and `scripts/`

Claude Code can read and edit any file in this repo, the same way you
would in a text editor — just faster, and with the whole repo as
context. Some things it's genuinely useful for here:

- **Explaining a mission script** — ask "walk me through what
  `grid_3d_flight_plan.py` does" and it reads the file and explains
  it, the same way `python-concepts-guide.md` teaches you to read one
  yourself (start at `main()`, work outward).
- **Making a small, well-scoped change** — e.g. "change
  `HOVER_SECONDS` in `altitude_square_demo.py` to 3" or "add a new
  waypoint to `waypoint_route.py`'s `WAYPOINTS` list." It makes the
  edit and shows you exactly what changed before moving on.
- **Checking your work before you fly** — ask it to run
  `python -m py_compile` on your new script, or check that it defines
  `main()` and wraps its flight logic in `try`/`finally`, matching
  what this repo's CI check (`.github/workflows/syntax-check.yml`) and
  `CONTRIBUTING.md` both require.
- **Drafting a new mission from scratch** — describe the flight path
  in plain English (takeoff point, altitude changes, pattern,
  landing), and it can write a first draft following the same
  structure as the existing scripts (config variables at the top,
  docstrings, `try`/`finally`, a `main()` at the bottom).

**What it can't do for you:** actually fly the drone, or know whether
your flight plan is safe for your specific room. Every mission script
in this repo is explicitly untested on hardware for exactly that
reason — Claude Code can help you write and syntax-check a script, but
a human still has to test-fly it cautiously, per the safety notes in
`README.md` and `CONTRIBUTING.md`.

## A realistic example, start to finish

> **You:** "Add a new mission script called `figure_eight.py` that
> flies a figure-eight pattern at 60cm altitude, following the same
> style as the other scripts in `missions/`."
>
> **Claude Code:** reads a couple of the existing mission scripts to
> match their structure and docstring style, writes the new file, runs
> `python -m py_compile` on it to confirm it's syntactically valid,
> confirms it defines `main()` and wraps the flight logic in
> `try`/`finally`, and shows you the full file.
>
> **You:** read through the script it wrote, test-fly it cautiously
> with propellers off first, then ask Claude Code to commit it on a
> new branch and open a pull request per `CONTRIBUTING.md` — it will
> show you each step and wait for your approval before pushing
> anything to GitHub.

## Using it from a browser instead (no install at all)

Everything above assumes Claude Code is installed somewhere (desktop
app, terminal, or IDE). There's also a version that runs entirely in
a browser, connected straight to your GitHub account, with nothing to
install — see
[`using-claude-code-online.md`](using-claude-code-online.md) in this
same folder. The one thing it can't do is anything requiring the
physical drone, since it runs in the cloud, not on a machine next to
your hardware.

## Where to learn more

- Official quickstart: https://docs.claude.com/en/docs/claude-code/quickstart
- Full documentation: https://docs.claude.com/en/docs/claude-code
- Inside a running Claude Code session, typing `/help` explains the
  commands available in that session.
- For anything Git/GitHub-specific that isn't about Claude Code
  itself, `getting-access-and-setup.md` in this same `docs/` folder is
  the reference.
