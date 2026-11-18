# Setup checklist

## Approvals / people
- [ ] DPO / ICT sign-off on data flow + classification (DATA_PROTECTION #10)
- [ ] Name owners: Ops (roster), HR (CallLog), backup admin, +1 per centre (GEB officer / centre head)
- [ ] Confirm retention period

## Build (order)
1. [ ] Roster: fill `templates/roster_template.csv` columns **in the gov-cloud workbook** (not locally on personal devices)
2. [ ] Create workbook tables from template; paste formulas (`docs/excel_formulas.md`); run verification in EXCEL_WORKBOOK.md
3. [ ] Export Roster as CSV on work device → open toolkit → validate → copy option lists. Delete CSV after
4. [ ] Build both FormSG forms (Absent, Late) per FORMSG_SPEC.md; add collaborators; store secret key
5. [ ] Plumber Pipe 1 (follow `docs/PLUMBER_SETUP_GUIDE.md`); test submission → row in `Subs` → HR View
6. [ ] Plumber Pipe 2 (Late) + Pipe 3 (HR email); test
7. [ ] Paste Schedule rows into `Schedule`
8. [ ] Dry run 1 day with 2–3 teachers; time the teacher flow (< 40 s target)
9. [ ] Brief teachers (Absent link, NONE rule) and +1s (Late link, reasons). Pin links in the right groups
10. [ ] Brief HR (HR View, CallLog, what each status means)

## Netlify (toolkit only)
- [ ] Repo private on GitHub; Netlify site from this repo; `netlify.toml` already sets publish dir + CSP
- [ ] Optional: Netlify password protection / restrict to staff

## Recurring
- **Yearly (start of year, admin/ops):** rebuild Roster → toolkit → replace options in both forms (+ new checkbox fields & logic if centres/classes change) → re-test Pipe 1/2 mapping → archive last year's `Subs`/`CallLog`
- Ad hoc (withdrawal, TDC change): edit Roster row → toolkit → update the affected options in both forms
- Monthly: archive `Subs`/`CallLog`
- Weekly: review "LATE (not flagged)" + late reasons → TDC feedback
