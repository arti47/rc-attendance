# CLAUDE.md — RC Attendance

Regional-centre attendance for MOE. Teachers flag absent/late students; HR gets home school + TDC contact automatically to locate missing students by 3:10pm.

## Hard rules
- **No real student/TDC data anywhere in this repo, chats, commits, tests or Netlify.** Dummy data only (`templates/roster_template.csv`). Real data lives only in gov-cloud FormSG / Plumber / M365 Excel.
- Never weaken `.gitignore` data rules or `netlify.toml` CSP. No server code, Netlify Functions, analytics or third-party scripts in the toolkit.
- User preference: terse, technical replies. Ask clarifying questions **one at a time** (AskUserQuestion).
- Log every new requirement/decision in `docs/DECISIONS.md` (append).

## Architecture
```
Teacher -> FormSG (1 form, Storage mode) -> Plumber Pipe 1 -> Excel `Subs` (1 row/submission)
Excel formulas: Roster x Subs -> Status/FlaggedAt/LateReason -> HR View + Summary
Plumber Pipe 2 (2:55 chaser) / Pipe 3 (3:05 HR digest) read `Summary`
Roster Toolkit (static, Netlify, in-browser) -> validates roster CSV, generates FormSG option lists
```
Read in order: `docs/DECISIONS.md` → `docs/WORKFLOW_AUDIT.md` → `docs/FORMSG_SPEC.md` → `docs/PLUMBER_PIPES.md` (+ `docs/PLUMBER_SETUP_GUIDE.md` click-by-click) → `docs/EXCEL_WORKBOOK.md` → `docs/DATA_PROTECTION.md` → `docs/SETUP_CHECKLIST.md`.

## Contracts (change together or things silently break)
- Student key: `Name (SCHOOLCODE) <Subject><Class>` — `studentKey()` in `tools/roster-toolkit/lib.js` == Roster `Key` formula in `scripts/build_workbook.py`.
- Centre/Class label: `Ddd | Centre | C<n>` — `centreClassLabel()` == Roster `CentreClass` formula == FormSG dropdown.
- FormSG values `E/M/S`, `Absent/Late`, `NONE - all present` == strings used in formulas.
- `Subs` columns == Plumber Pipe 1 mapping.

## Layout
- `tools/roster-toolkit/` static app (`lib.js` pure logic, `app.js` UI, `index.html`)
- `tests/*.test.mjs` node tests for lib.js
- `scripts/build_workbook.py` → `templates/RC_Attendance_Template.xlsx` + `docs/excel_formulas.md` (FORMULAS list is source of truth)
- `data/schedule.csv` centre/day/class/zone (public school names only)

## Commands
- Test: `npm test`
- Rebuild template + formula doc: `python3 scripts/build_workbook.py` (needs openpyxl)
- Local preview: `cp data/schedule.csv tools/roster-toolkit/ && npx serve tools/roster-toolkit` (or `python3 -m http.server -d tools/roster-toolkit`)

## Status
Specs + toolkit + template done. Excel formulas not yet verified in live Excel; Plumber [verify] items open. See Open items in `docs/DECISIONS.md`.
