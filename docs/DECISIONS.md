# Decisions log (append-only; newest at bottom)

Requirements gathered 2026-11-18:
- Daily E/M/S classes at regional centres; schedule in `data/schedule.csv` (Mon–Thu only, confirmed).
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
- ~~O2~~ → D7.
- ~~O3~~ → D9 (keep 2:50).
- ~~O4~~ → D11.
- O5 Verify Plumber features marked [verify] in PLUMBER_PIPES.md.

2026-11-18 (Q11):
- D6 Form access = open link + Email field with OTP verification, restricted to MOE domains. Relief teachers must be able to submit without pre-registration. Singpass and whitelist rejected. `Subs.SubmittedBy` = verified email (audit trail).

2026-11-18 (Q12):
- D7 HR 3:05pm email = missing count + workbook link only. No student names/phones in any email.

2026-11-18 (Q13):
- D8 2:55pm not-submitted email → centre head (chases teachers). Backup in CC recommended. Absent cut-off change (O3) still open.

2026-11-18 (Q14):
- D9 No 2:55 chaser email (supersedes D8). Each centre has a "+1" (GEB officer or centre head) who walks around at 3pm.
- D10 Two submissions: 2:50 Absent by subject teachers (form "RC Absent"); 3:00 Late by the +1 (form "RC Late", one per centre, all students of that centre, free-text reason).
- Late matching in Excel = date + key (centre-wide), not scoped by class/subject.

2026-11-18 (Q15):
- D11 Classes run Mon–Thu only. Pipe 3 scheduler = Mon–Thu 15:05.

2026-11-18 (Q16):
- D12 HR call outcomes (CallLog dropdown): Located - at home school; Located - at home; Absent - valid reason (MC/leave); No answer - retry; Not located - escalated. Summary.UnresolvedCount tracks the rest.

2026-11-18 (Q17):
- D13 Roster owner = admin/ops; full rebuild once a year (start of year). Ad-hoc fixes (withdrawals, TDC change) by admin/ops: edit Roster → toolkit → update options in both forms.
