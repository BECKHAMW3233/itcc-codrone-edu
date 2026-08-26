# Using Claude Code Online (claude.ai/code) With GitHub

This is the companion to [`using-claude-code.md`](using-claude-code.md)
in this same folder — read that one first if you haven't, since this
page assumes you already know the basics (chatting in plain English,
reviewing diffs before changes are made). This page covers the
**online version**: doing all of it from a browser, connected to your
GitHub account, with nothing installed on your computer at all.

## The one thing that matters most for this specific repo

Claude Code online runs your session in a temporary cloud computer,
not on your physical machine — so **it has no access to your CoDrone
EDU drone or USB Bluetooth dongle.** You can use it to write, edit,
review, and syntax-check mission scripts (everything short of
actually flying), and to fully manage Git/GitHub for this
repo — branches, commits, pull requests. But the real test-flight step
that `CONTRIBUTING.md` requires still has to happen on a computer
physically near the drone, either using
[`using-claude-code.md`](using-claude-code.md)'s local version or just
running the script yourself once it's on your machine.

## How it's different from the local version

- **No install.** You open a browser tab at claude.ai/code — nothing
  to download, no terminal.
- **It clones the repo for you, fresh, every session** — you don't
  need this repo checked out locally at all to use this version.
- **Sessions keep running even if you close the tab.** Start a task,
  close your laptop, check back later (even from your phone) to
  review what it did.
- **Permission works differently.** The local version asks you to
  approve each risky action individually as it comes up (see
  `using-claude-code.md`). The online version instead has you pick one
  of three modes *before* the session starts:
  - **Plan** — Claude proposes an approach first and waits for you to
    approve it before touching any files. **This is the one to pick
    if you're new to this** — you see what it intends to do before
    anything happens.
  - **Accept edits** — Claude makes changes and pushes its branch
    without stopping to ask. Faster, but you're reviewing everything
    *after* the fact instead of before.
  - **Auto** — a classifier reviews Claude's actions instead of you;
    only shows up if your organization has this turned on.

  Whichever mode you pick, it always works on its own new branch, not
  directly on `main` — and now that this repo has real branch
  protection turned on, nothing can land in `main` without a pull
  request and a review, no matter which mode was used to create it.

## Connecting your GitHub account (one-time setup)

1. Go to [claude.ai/code](https://claude.ai/code) and sign in with
   your Anthropic/Claude account.
2. The first time, it'll prompt you to connect GitHub — follow the
   prompt to install the **Claude GitHub App** and grant it access to
   your repositories. You can choose to grant access to all your
   repos or just specific ones; picking just `itcc-codrone-edu` (and
   any others you actually plan to use this with) is the more
   privacy-conscious choice.
3. You'll be asked to confirm a **cloud environment** (it creates a
   "Default" one automatically) — this just controls things like
   network access during sessions. The default settings are fine to
   start with.

Connecting your GitHub account here doesn't grant you any repo access
you didn't already have — if you're not yet a collaborator on this
repo, sort that out first via Part 1 of
[`getting-access-and-setup.md`](getting-access-and-setup.md).

## Starting a task on this repo

1. From claude.ai/code, click the repository selector and choose
   `itcc-codrone-edu`.
2. Pick a branch to start from — usually `main` for new work, or an
   existing branch if you're continuing something already in
   progress.
3. Pick a permission mode (see above — **Plan** if you're not sure).
4. Type a specific description of what you want and submit it. Be
   concrete: "Add a new mission script `figure_eight.py` following the
   style of the other files in `missions/`" works much better than
   "make a new mission."

Claude clones the repo into its cloud session and gets to work. You
can watch it in real time, or step away and come back later.

## Reviewing the result and opening a pull request

When Claude reaches a stopping point (or finishes), it pushes its
branch to GitHub automatically — this is a real branch push, but
still just a branch, not `main`.

1. Open the **diff view** to see exactly what changed, file by file.
2. You can click any changed line and leave an inline comment — e.g.
   "this should hover for 5 seconds like the other scripts, not 3" —
   and it'll address your comments the next time you send a message.
3. When it looks right, click **Create PR** at the top of the diff
   view. It'll generate a title and description for you, which you
   can edit before submitting — same pull request process described
   in `CONTRIBUTING.md`, just started from the browser instead of the
   command line.
4. The session stays open after the PR is created — if GitHub's
   `syntax-check` CI check fails, or a club member leaves review
   comments on the PR, you can paste that feedback back into the same
   chat and ask Claude to fix it.

## A realistic example

> You open a session on `itcc-codrone-edu` from your phone between
> classes, pick **Plan** mode, and ask "add a short comment to
> `waypoint_route.py` explaining what `ROTATIONAL_VELOCITY_DEG_PER_SEC`
> controls." It proposes exactly what it'll change; you approve it; it
> edits the file, pushes a branch, and shows you the diff. You open
> **Create PR** right from your phone.
>
> That evening, with the drone actually in front of you, you pull that
> branch locally (or wait for it to merge) and test-fly it — the one
> part that had to wait for hardware.

## Where to learn more

- Official quickstart: https://code.claude.com/docs/en/web-quickstart
- [`using-claude-code.md`](using-claude-code.md) — the local-machine
  version of this guide, with a fuller explanation of how Claude
  Code's permission model works in general
- [`getting-access-and-setup.md`](getting-access-and-setup.md) — for
  getting collaborator access to this repo in the first place
