# Getting Access & Setting Up — ITCC CoDrone EDU Repo

This is the onboarding guide for new ITCC members joining this
project. It covers two things: how to get added to the repo as a
collaborator, and how to get the code running on your own machine
once you have access. For how to actually submit a mission once
you're set up, see `CONTRIBUTING.md`.

---

## Why this is worth learning properly, not just following along

The mechanics below — cloning, branching, committing, pull requests —
aren't just steps to get through so you can fly a drone. Git and
GitHub are the actual, industry-standard way that professional
software and cybersecurity teams manage code, track changes, and
collaborate, whether you end up writing code day-to-day or not.

A few concrete reasons this matters beyond this club project:

- **Version control is a real job skill.** Almost every technical
  role — developer, sysadmin, security analyst, DevOps, IT support —
  touches Git in some form. Knowing how to clone a repo, work on a
  branch, and open a pull request without help is a baseline
  expectation, not a specialized skill.
- **This workflow mirrors how real teams operate.** Branch protection,
  required reviews, and automated checks (like the syntax check this
  repo runs on every pull request) exist here for the same reasons
  they exist at a real company: to catch mistakes before they reach
  everyone else's code, and to make sure more than one person looks
  at a change before it ships.
- **A GitHub profile is a portfolio.** A federal hiring manager,
  internship coordinator, or interviewer can look at your GitHub
  account and see real, dated evidence of work — commits, pull
  requests, code you wrote and got reviewed. That's harder evidence
  of ability than a bullet point on a resume, and it costs nothing
  extra to build if you're already doing the work here properly.
- **Mistakes here are cheap; mistakes on the job aren't.** This is a
  low-stakes place to get comfortable with things like "I pushed to
  the wrong branch" or "my pull request failed a check" — better to
  work through that confusion on a club project than for the first
  time on a paid job.

None of this requires being an expert going in. It requires actually
doing the steps below yourself — cloning, branching, committing,
opening pull requests — rather than having someone else do it for
you, so the muscle memory is real by the time it matters somewhere
else.

---

## Part 1: Getting repo access

This repo uses **direct collaborator access** — once you're added,
you can push branches and open pull requests yourself. You do not
need to fork the repo.

### If you don't have a GitHub account yet

1. Go to [github.com](https://github.com) and sign up (it's free).
2. Send your GitHub **username** (not your email) to the repo owner
   so they can add you.

### Getting added as a collaborator

1. Send your GitHub username to the repo owner/maintainer.
2. They'll add you under the repo's **Settings → Collaborators and
   teams**. You'll receive an email invite from GitHub.
3. **Accept the invite** — check your email, or go to
   `github.com/YOUR-USERNAME` and look for a notification banner.
   You won't have push access until you accept.
4. Once accepted, you can clone the repo and push branches directly
   (see Part 2 below).

### What collaborator access gives you

- Clone the repo (or you could already do this if it's public —
  collaborator access is about *pushing*, not just reading)
- Create and push your own branches
- Open pull requests
- Comment on and review other members' pull requests

### What it does NOT give you

- Direct push access to `main` is blocked by branch protection —
  all changes go through a pull request, even for collaborators.
  This is intentional: it keeps a review step and the automated
  syntax check in front of every change, including yours.

---

## Part 2: Setting up the repo locally

### Requirements

- **Git** installed on your machine
  ([git-scm.com](https://git-scm.com) if you don't have it)
- **Python 3.8+** installed
- **A GitHub account with collaborator access** (see Part 1)
- If you're planning to test-fly a mission: a CoDrone EDU + USB
  Bluetooth dongle, physically with you

**Never typed a Git command before?** That's expected — CTI-110 and
most intro IT coursework don't cover this. Everything below still
works, it'll just be new. If typing commands feels intimidating, you
can skip straight to
[`using-claude-code.md`](using-claude-code.md) instead, which lets
you do all of this (clone, branch, commit, push) by describing what
you want in plain English rather than memorizing commands. This
section is still worth skimming even then, since it explains what's
actually happening underneath.

### What's a terminal, and how do I open one?

A **terminal** (also called a command line or, on Windows, a
"console") is a plain text window where you type commands instead of
clicking buttons — it's how `git` commands actually get run. You
don't need to be comfortable with it beyond copy-pasting the commands
in this guide.

- **Windows:** Installing Git (above) also installs **Git Bash**.
  Open the folder where you want the repo in File Explorer,
  right-click inside it, and choose **"Git Bash Here"** — or search
  "Git Bash" in the Start menu. Either way, a terminal window opens
  and you can type the commands below into it.
- **Mac:** Press `Cmd + Space`, type `Terminal`, and press Enter. This
  opens a terminal you can `cd` into your project folder from (see
  the `cd` command below), or type the commands directly.

Every gray code box in this guide is something you type into that
window, one line at a time, pressing Enter after each line.

### Cloning the repo

In your terminal, run:

```bash
git clone https://github.com/BECKHAMW3233/itcc-codrone-edu.git
cd itcc-codrone-edu
```

The first line downloads a full copy of the repo (with its entire
history) into a new `itcc-codrone-edu` folder wherever your terminal
is currently pointed. The second line (`cd`, short for "change
directory") moves your terminal *into* that new folder, so the
commands you run next apply to the repo instead of wherever you
started.

### Installing dependencies

```bash
pip install -r requirements.txt
```

This installs the `codrone-edu` Python package needed to run any
mission script.

### Confirming it works

Try the distance converter first — it needs no drone, just Python:

```bash
python scripts/converter.py
```

If that runs and lets you convert a value, your Python setup is
working. When you're ready to test an actual mission (drone paired
and nearby):

```bash
python missions/altitude_square_demo.py
```

### What do I actually edit `.py` files with?

Any plain text editor technically works — Notepad on Windows, or
TextEdit in plain-text mode on Mac. In practice, a free **code
editor** makes this much easier and is worth installing:

- **VS Code** ([code.visualstudio.com](https://code.visualstudio.com))
  — free, works on Windows/Mac/Linux, color-highlights Python so
  mistakes stand out, and has a built-in terminal so you can edit and
  run a script from the same window.

To make a change: open the `.py` file in your editor, find the
variable you want to change (e.g. `TARGET_GRID = (10, -6)` near the
top of `grid_flight_plan.py` — every mission script's editable values
live in a `# ---- Configuration ----` section near the top), edit the
value, save the file (`Ctrl+S` / `Cmd+S`), then run it again from your
terminal the same way you did above.

If you'd rather not touch an editor directly, see
[`using-claude-code.md`](using-claude-code.md) — you describe the
change you want in plain English and it edits the file for you.

### Making your own changes: branch, don't push to main

Direct pushes to `main` are blocked, so every change — even a small
one — goes through a branch and a pull request:

```bash
# make sure you're starting from the latest main
git checkout main
git pull

# create a branch for your work
git checkout -b yourname-mission-name

# ... write your mission script, test it ...

git add missions/your_script.py
git commit -m "Add [short description of the mission]"
git push -u origin yourname-mission-name
```

Then go to the repo on GitHub — it'll show a banner offering to open
a pull request from your new branch. Click it, fill in the
description (see `CONTRIBUTING.md` for what to include), and submit.

Your PR will automatically run the repo's syntax check. Once it
passes and someone reviews it, it can be merged into `main`.

### Keeping your local copy up to date

Before starting new work, pull the latest changes from `main` so
you're not working from a stale copy:

```bash
git checkout main
git pull
```

Do this regularly, especially before starting a new branch.

### If something goes wrong

- **`git push` is rejected / permission denied** — you likely haven't
  accepted your collaborator invite yet, or the invite hasn't been
  sent. Check your email, or ask the repo owner to confirm you're
  listed under Settings → Collaborators on the repo.
- **Push to `main` is rejected** — this is expected and intentional
  (branch protection). Create a branch and open a pull request
  instead — see above.
- **`pip install -r requirements.txt` fails** — make sure you're
  running a supported Python version (`python --version`, should be
  3.8+), and that `pip` is pointing at that same Python install.
- **Drone won't pair** — check the USB Bluetooth dongle is plugged
  in, the drone is powered on, and the battery isn't dead. This is a
  hardware/pairing issue, not a repo issue.

---

## Quick reference

| Task | Command |
|---|---|
| Clone the repo | `git clone https://github.com/BECKHAMW3233/itcc-codrone-edu.git` |
| Install dependencies | `pip install -r requirements.txt` |
| Update your local `main` | `git checkout main && git pull` |
| Start a new branch | `git checkout -b yourname-mission-name` |
| Push your branch | `git push -u origin yourname-mission-name` |
| Run the unit converter | `python scripts/converter.py` |
| Run a mission (drone required) | `python missions/<script-name>.py` |
