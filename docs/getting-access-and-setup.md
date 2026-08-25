# Getting Access & Setting Up — ITCC CoDrone EDU Repo

This is the onboarding guide for new ITCC members joining this
project. It covers two things: how to get added to the repo as a
collaborator, and how to get the code running on your own machine
once you have access. For how to actually submit a mission once
you're set up, see `CONTRIBUTING.md`.

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

### Cloning the repo

Open a terminal and run:

```bash
git clone https://github.com/YOUR-USERNAME/itcc-codrone-edu.git
cd itcc-codrone-edu
```

Replace `YOUR-USERNAME` with the actual GitHub username/org that
owns the repo — get the exact URL from the green "Code" button on
the repo's GitHub page.

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
| Clone the repo | `git clone <repo-url>` |
| Install dependencies | `pip install -r requirements.txt` |
| Update your local `main` | `git checkout main && git pull` |
| Start a new branch | `git checkout -b yourname-mission-name` |
| Push your branch | `git push -u origin yourname-mission-name` |
| Run the unit converter | `python scripts/converter.py` |
| Run a mission (drone required) | `python missions/<script-name>.py` |
