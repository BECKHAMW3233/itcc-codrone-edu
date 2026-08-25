# CoDrone EDU Official Resources (Links Only)

This folder is an index of Robolink's own official CoDrone EDU
documentation and materials — the user manual, technical specs, and
support resources. **These are Robolink's copyrighted materials, not
this club's** — this folder links to them rather than copying them in,
since redistributing someone else's proprietary documentation isn't
something this repo can do. Bookmark this page, or the links directly,
for offline-adjacent convenience; the actual content always lives at
Robolink's site and is best read there so you get their latest
version.

If a link below ever breaks, search "CoDrone EDU" plus the resource
name — Robolink occasionally reorganizes their docs site.

## User manual

- **Digital User Manual (web version):**
  https://docs.robolink.com/docs/CoDroneEDU/Resources/Digital-User-Manual/
- **User Manual (PDF, v3.2):**
  https://docs.robolink.com/files/co-drone-edu-manual-v-3-2.pdf

  Covers unboxing, charging, controller pairing, basic flight controls,
  and safety guidelines for the physical drone itself — start here for
  anything hardware-related that isn't about Python code.

## Developer / API documentation

- **CoDrone EDU docs home:** https://docs.robolink.com/docs/CoDroneEDU/
- **Python SDK reference:** https://docs.robolink.com/docs/CoDroneEDU/Python/

  This is the full API documentation for every function used in this
  repo's `missions/` scripts (`takeoff()`, `move_forward()`,
  `send_absolute_position()`, sensor functions, etc.). This repo's own
  [`../docs/sdk-quick-reference.md`](../docs/sdk-quick-reference.md) is
  a short cheat sheet built from this — come here for anything it
  doesn't cover.

## Technical specifications

- **CoDrone EDU technical specs (PDF):**
  https://docs.robolink.com/assets/files/cde_technical_specifications_v_1_1-87fc0793f9205a596e820f78b19ca846.pdf

  Physical specs — dimensions, weight, battery, sensor ranges, radio
  range — useful when deciding whether a mission's distances/altitudes
  are realistic for the hardware.

## Support

- **Robolink help center:** https://help.robolink.com

  For anything hardware-broken, pairing issues beyond what
  `../docs/getting-access-and-setup.md`'s troubleshooting section
  covers, or warranty/order questions — this is Robolink's own support
  channel, not something this club can resolve.

## A note on keeping a personal copy

Robolink's manual page itself recommends having your user manual on
hand during class or competition. If you want a personal offline copy
for that reason, download the PDF above directly from Robolink's site
to your own device — that's using it the way they intend. What this
repo avoids is re-hosting a copy *inside the shared club codebase*,
since that's redistribution rather than personal use, and isn't ours
to grant.
