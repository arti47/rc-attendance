# Excel workbook (gov-cloud M365, owned via Plumber connection)

Template (dummy data): `templates/RC_Attendance_Template.xlsx` — built by `python3 scripts/build_workbook.py`.
Formulas: `docs/excel_formulas.md` (auto-generated; also on the template's `Formulas` sheet).
If Plumber requires its own file, recreate the same tables/headers in it and paste formulas.

## Tables
| Table | Owner | Purpose |
|-------|-------|---------|
| `Roster` | Ops (manual) | Master list. Input cols: StudentName, HomeSchool, SchoolCode, Day, Centre, Class, Subject, TDCName, TDCPhone. Formula cols: Key, CentreClass, AbsentToday, LateToday, Status, FlaggedAt, LateReason, HROutcome |
| `Subs` | Plumber only | 1 row per FormSG submission. Format `SubmittedAt`, `Date` columns as Text |
| `Schedule` | Ops | Day, CentreClass, Subject (paste from toolkit) + formula `Submitted` |
| `CallLog` | HR | Date, StudentKey (copy from HR View last col), Outcome, CalledBy, Notes |
| `Summary` | Formulas | Metric/Value rows read by Plumber pipes 2 & 3 |
| HR View sheet | Formula | Spill at A2: today's flagged students, MISSING first, read-only |

## Status logic
| Absent today | Late today | Status |
|---|---|---|
| yes | no | MISSING → HR calls |
| yes | yes | ARRIVED LATE |
| no | yes | LATE (not flagged) — teacher didn't flag absent at 2:50 (feedback item) |

## Design choices
- Matching is scoped by Date + Type + CentreClass + Subject, and by `,Key,` delimiters → no cross-centre or substring false matches.
- `SUMPRODUCT`/`FIND` used instead of `COUNTIFS` (COUNTIFS fails on cells > 255 chars).
- Rows only compute when `Day` = today → fast.
- No daily reset needed: everything filters on TODAY().
- Monthly: move old `Subs`/`CallLog` rows to an archive sheet to keep it fast; delete per retention policy.

## First-build verification (formulas untested in live Excel)
1. Paste formulas; confirm no `#NAME?` (needs Excel for the web / M365, not Excel 2016).
2. Add a fake Roster row with today's Day; add a `Subs` row manually with its Key → Status = MISSING, HR View shows it.
3. Add a Late row → ARRIVED LATE + reason.
4. Check `Schedule[Submitted]` and `Summary` values.
5. Delete test rows.
