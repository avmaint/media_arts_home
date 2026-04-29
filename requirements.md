---
title: "Media Arts Home — Requirements"
---

# Overview

A Flask-based internal home page served on port 80 from `uacts-g001` / `cumu-g001`.
Purpose: single index of all services, tools, and documentation used by the UAC Media Arts team.
No authentication required; open access on the LAN.

---

# Functional Requirements

## MA-01 — Service Index
The home page shall display all team services grouped into three categories: **Operational**, **Administration**, and **Reference**. Each service is displayed as a card showing an icon, name, and short description.

## MA-02 — External Links
Clicking a service card shall open its URL in a new browser tab. Cards with no URL configured (status: TBD) shall not be clickable and shall display a "TBD" badge.

## MA-03 — UAC Branding
The page header shall display the UAC cross logo and the title "Media Arts". Styling follows the UAC website colour scheme (primary blue `#0052cc`).

## MA-04 — Configuration-Driven
All service data (name, URL, description, icon, category) shall be stored in `config.json`. No code change is needed to add, remove, or update a service — only `config.json` requires editing.

## MA-05 — Manual / PDF Index (Future)
The system shall provide an index mapping asset tags to PDF manuals, accessible from the Reference section. Implementation deferred.

## MA-06 — NDI Device Links (Todo)
NDI Transmitter and NDI Receiver shall be listed under Administration once their IPs are confirmed in network.xlsx.

## MA-07 — System Documentation Link (Todo)
A link to the HTML-generated technical documentation shall be added to the Reference section once its URL is confirmed.

---

# Service Inventory

## Operational

| Name | URL | Asset Tag |
|---|---|---|
| CueCommander | http://uacts-g001:1880 | — |
| AVL Assistant | http://uacts-g001:9000 | — |
| Companion | http://cumu-g001:8000/emulator/QILZbNAkPdKxFfqRmpvMs | — |
| Planning Centre | https://services.planningcenteronline.com | — |
| ProPresenter Control | http://192.168.0.210:1025/v1/control/ | — |
| Lighting Console | http://192.168.0.197:8080 | ZLKU-C001 |
| Resi | https://studio.resi.io | — |
| Kaleo AI | http://getkaleo.ai | — |
| Church Motion Graphics | https://www.churchmotiongraphics.com | — |
| SongSelect | https://songselect.ccli.com/search/ | — |
| Kramer Matrix | http://192.168.206.7 | ZVKU-A001 |
| PTZ Camera 1 | http://192.168.0.186 | ZVCU-A001 |
| PTZ Camera 2 | http://192.168.0.187 | ZVCU-A002 |
| PTZ Camera 3 | http://192.168.0.188 | ZVCU-A003 |
| Projector — Confidence | http://192.168.0.183 | ZVVU-0001 |
| Projector — FoH East | http://192.168.0.193 | ZVVU-A001 |
| Projector — FoH Centre | http://192.168.0.194 | ZVVU-A002 |
| Projector — FoH West | http://192.168.0.195 | ZVVU-A003 |

## Administration

| Name | URL | Asset Tag |
|---|---|---|
| Omada Controller | https://192.168.201.2/#dashboardGlobal | — |
| Switch NSCU-A001 | http://192.168.0.22 | NSCU-A001 |
| Switch NSCU-A002 | http://192.168.0.23 | NSCU-A002 |
| Switch NSCU-A003 | http://192.168.0.24 | NSCU-A003 |
| Switch NSCU-A004 | http://192.168.0.25 | NSCU-A004 |
| Switch NSCU-A005 | http://192.168.0.26 | NSCU-A005 |
| Q-SYS Core (Local) | https://192.168.200.50 | — |
| Q-SYS Reflect | https://reflect.qsc.com/login | — |
| NDI Transmitter | TBD | — |
| NDI Receiver | TBD | — |

## Reference

| Name | URL | Notes |
|---|---|---|
| MXU Training | http://getmxu.com | AV skills training platform |
| System Documentation | TBD | HTML-generated docs |
| Equipment Manuals | TBD | PDF index by asset tag (future) |

---

# Deployment

- Server: `uacts-g001` (alias `cumu-g001`)
- Port: 80 (requires root or `CAP_NET_BIND_SERVICE`)
- Start: `sudo python3 app.py`
- Config: edit `config.json` to add/update/remove services; no restart needed (config is reloaded on each request)
