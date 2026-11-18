# Decisions log (append-only; newest at bottom)

Requirements gathered 2026-11-18:
- Daily E/M/S classes at regional centres; schedule in `data/schedule.csv` (Mon–Thu shown; add Fri if any).
- Constraints: MOE data rules; data stays on gov cloud. Stack: FormSG → Plumber → M365 Excel (gov cloud). Netlify later for code only.
- Teachers have ~1 min. They tick **absentees only** from a dropdown/checkbox (no free text, no school selection).
- 2:50pm absent submission; 3:00pm latecomer submission which checks students off the absent list; late form needs free-text reason (internal log, TDC feedback).
- HR needs student → home school → TDC name + phone auto-populated by 3:10pm.
- No master roster existed → create in gov cloud.
- 3 subject groups (E/M/S) run in parallel per centre-class, each teacher submits own group.
- Student identifier: Name + school code + subject/class, e.g. `Alex Tan (DPS) M1`.
- Alerts wanted: HR email digest, non-submission chaser, live sheet.
- Tools beyond FormSG/Plumber/Excel: unknown → design uses only those + optional static toolkit.

Design decisions:
- D1 One form + one pipe (was one form per centre). Single link teachers can forward.
- D2 Plumber writes 1 row/submission; Excel formulas do lookups/status (no Plumber loops).
- D3 `NONE - all present` mandatory option → enables non-submission detection.
- D4 Status MISSING / ARRIVED LATE / LATE (not flagged).
- D5 Roster toolkit = static, client-side, CSV only, no deps.

Open:
- ~~O1~~ → D6.
- O2 PII in HR digest email?
- O3 Move absent cut-off to 2:45?
- O4 Friday schedule?
- O5 Verify Plumber features marked [verify] in PLUMBER_PIPES.md.

2026-11-18 (Q11):
- D6 Form access = open link + Email field with OTP verification, restricted to MOE domains. Relief teachers must be able to submit without pre-registration. Singpass and whitelist rejected. `Subs.SubmittedBy` = verified email (audit trail).
