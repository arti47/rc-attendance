# Setup checklist

## Approvals / people
- [ ] DPO / ICT sign-off on data flow + classification (DATA_PROTECTION #10)
- [ ] Name owners: Ops (roster), HR (CallLog), backup admin, centre head backup (2:55 email CC)
- [ ] Confirm retention period

## Build (order)
1. [ ] Roster: fill `templates/roster_template.csv` columns **in the gov-cloud workbook** (not locally on personal devices)
2. [ ] Create workbook tables from template; paste formulas (`docs/excel_formulas.md`); run verification in EXCEL_WORKBOOK.md
3. [ ] Export Roster as CSV on work device → open toolkit → validate → copy option lists. Delete CSV after
4. [ ] Build FormSG per FORMSG_SPEC.md; add collaborators; store secret key
5. [ ] Plumber Pipe 1 (follow `docs/PLUMBER_SETUP_GUIDE.md`); test submission → row in `Subs` → HR View
6. [ ] Plumber Pipes 2 & 3; test emails
7. [ ] Paste Schedule rows into `Schedule`
8. [ ] Dry run 1 day with 2–3 teachers; time the teacher flow (< 40 s target)
9. [ ] Brief teachers (1-page: link, steps, NONE rule, late reason). Pin link in staff group
10. [ ] Brief HR (HR View, CallLog, what each status means)

## Netlify (toolkit only)
- [ ] Repo private on GitHub; Netlify site from this repo; `netlify.toml` already sets publish dir + CSP
- [ ] Optional: Netlify password protection / restrict to staff

## Recurring
- Term start / roster change: update Roster → toolkit → update FormSG options (+ new checkbox field & logic if a new centre-class)
- Monthly: archive `Subs`/`CallLog`
- Weekly: review "LATE (not flagged)" + late reasons → TDC feedback
