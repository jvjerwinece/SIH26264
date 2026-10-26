# PS 26264 mapping

**Problem statement:** Integrated Dashboard for Monitoring and Tracking Institution-Related Complaint Cases Across AICTE Bureaus/Cells.

The statement names eight things authorized AICTE officials should be able to do. All eight are demoable in v8. This document maps each one to the screen and the data behind it, and flags what is prototype-only.

---

## 1. The eight objectives

| # | Objective (portal wording) | Where it lives in v8 | Data / mechanism | Video cue |
|---|---|---|---|---|
| 1 | View all institution-related complaint/grievance cases in one place | **Dashboard**, **All Cases** | `cases` + `institutions`; `v_case_register` | Open on the dashboard; point to the single register |
| 2 | Identify the Bureau/Cell currently handling each case | Bureau chip on every case card; **Institution Profile** custody line; **Rooms** lead bureau | `cases.bureau`, `cases.officer_id`, `rooms.lead_bureau` | Point to the RB/PGRC chip and named officer |
| 3 | Track the complete status and movement of a complaint/case | Case cards, **Institution Profile** timeline, **All Cases** status filter | `cases.status`, `case_events` (append-only) | Open one case's history |
| 4 | Identify cases where RB and PGRC actions overlap or multiple Bureaus/Cells deal with the same institution | **Overlap Radar** | `overlap_clusters` (confidence, `reason` JSON), `overlap_cases` | Show CL-01 with both bureaus and the reasons |
| 5 | Avoid duplication of action and ensure coordination between Bureaus/Cells | **Case Intake** collision check; **Create joint case**; **Coordination Rooms**; merge with `duplicate_of`; printable brief | `overlap_clusters`, `rooms`, `room_activity`, `cases.duplicate_of` | Load sample → open cases → joint case → room decision |
| 6 | Monitor pending, disposed, under-process, transferred and escalated cases | Dashboard KPI row; **All Cases** filters; status pills | `cases.status` constrained to the five states; `cases.transfer_to` required for transfers | Filter by status, show all five |
| 7 | Generate institution-wise, region-wise, Bureau/Cell-wise and status-wise reports | **Reports & analytics** | `v_case_register` (`institution`, `region`, `bureau`, `status`), bar panels, CSV export | Apply a region filter, export CSV |
| 8 | Provide alerts for pending cases and cases approaching prescribed timelines | Dashboard **Alerts & notifications**; **Reports** "Beyond timeline" KPI | `sla_days`, `received_on`, `beyond_sla`, `next_action` | Show the SLA breach and the case due in 5 days |

## 2. Key features expected

| Feature | Status | Notes |
|---|---|---|
| Centralized institution profile with AICTE Permanent ID | Built | Permanent ID is the key; profile shows name, address, region, trust and consolidated history |
| Consolidated case history per institution | Built | Institution Profile aggregates all cases across bureaus |
| Unique case ID, receipt date, category, status, bureau, officer | Built | All fields present and seeded |
| Real-time status and movement | Demo-level | State is in-browser; a production build needs the API in `ARCHITECTURE.md` |
| Duplicate/overlap detection | Built | Alias graph + trigram; confidence and human-readable reasons |
| Coordination between bureaus | Built | Room, lead bureau, joint decision, escalation reason, merge target |
| Reports and export | Built | Institution/region/bureau/status filters; CSV export |
| Alerts and timeline monitoring | Built | Dashboard alerts; `beyond_sla` computed at read time |
| Role-based access for authorized officials | **Not built** | Role selector in the prototype is a demo affordance, not authentication. Must be built before any pilot |
| Audit and accountability | Partially built | PostgreSQL chain is sound; browser verifier has P1-1; see `QA_REPORT.md` |

## 3. How the model answers the statement's core complaint

The statement's diagnosis is: same institution, different bureaus, no central real-time view, overlapping action, duplication, delays, unclear ownership.

| Diagnosis | Ekasutra response |
|---|---|
| Cases for the same institution sit in different cells | One institution thread keyed on Permanent ID |
| No real-time status | One register, one status vocabulary, one SLA clock |
| Overlapping action | Overlap Radar classifies duplicate / related / conflict / systemic |
| Duplication of effort | Intake collision check; joint case; merge with retained link |
| Delay in disposal | `age_days`, `beyond_sla`, next action, alerts |
| Unclear ownership | Bureau + officer + lead bureau + custody, visible on the case and the room |
| Weak accountability | Append-only actions and a hash chain, with a printable decision brief |

## 4. Demo path that covers all eight in under three minutes

1. **Dashboard** — eight objectives in one glance: register, bureau split, SLA breach, overlap alert. (1, 2, 6, 8)
2. **Case Intake → Load sample → Resolve & check** — identity resolution and open cases at the same institution. (1, 5)
3. **Create joint case → Coordination Room CR-01** — lead bureau, joint decision, activity. (2, 5)
4. **Escalate or merge duplicate** — reason required; absorbed case stays linked. (3, 5, 6)
5. **Institution Profile** — one thread across RB and PGRC. (1, 3)
6. **Reports** — filter by region/bureau/status; export. (7)
7. **Audit Log → Verify chain; Data Layer** — proof. (accountability)

## 5. What not to claim

- Do not claim role-based access is implemented. The role selector changes the demo persona; there is no authentication or authorization.
- Do not claim a live multi-user deployment. The prototype is single-browser, offline, `localStorage`.
- Do not claim national-scale matcher performance. See `DATA_NOTICE.md`.
- Do not claim the production stack is built. It is a target architecture.

## 6. Coverage summary

| Measure | Result |
|---|---|
| Portal objectives demoable | **8 / 8** |
| Key features built in prototype | 8 of 9 (RBAC not built) |
| PS fit | Strong: institution-first model directly addresses the overlap/ownership diagnosis |
| Production readiness | Low: no auth, API, or live database connection |
