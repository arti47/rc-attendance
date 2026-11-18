# Plumber pipes

Workbook: M365 Excel on gov cloud (Plumber connection). Tables: `Roster`, `Subs`, `Schedule`, `CallLog`, `Summary` (see EXCEL_WORKBOOK.md).
Items marked **[verify]** depend on Plumber features — confirm in the Plumber UI / guide (guide.plumber.gov.sg) on first build.

## Pipe 1 — RC Attendance Intake (event)
| Step | App / action | Config |
|------|--------------|--------|
| Trigger | FormSG → New form response | Paste Plumber webhook URL into FormSG Settings → Webhooks |
| 1 | Formatter → Date/time → Format **[verify]** | Input: submission time. Format `yyyy-MM-dd`, timezone Asia/Singapore → `Date` |
| 2 | M365 Excel → Create table row | Table `Subs`. Map: `SubmittedAt` = submission time (HH:mm SGT); `Date` = step 1; `Type` = Report type; `CentreClass` = Centre / Class; `Subject` = Subject; `Students` = **all checkbox fields concatenated** (only one non-empty); `Reason` = Reason field; `SubmissionID` = response ID; `SubmittedBy` = Staff email |

No loops, no lookups: Excel formulas do the rest.
If step 1 unavailable: write raw timestamp to `Date`; Excel uses `TEXT(Subs[Date],"yyyy-mm-dd")` — verify the timezone is SGT.

## Pipe 2 — Non-submission chaser (2:55pm Mon–Fri)
| Step | App / action | Config |
|------|--------------|--------|
| Trigger | Scheduler → weekdays 14:55 **[verify]** | |
| 1 | M365 Excel → Get table row | `Summary`, lookup `Metric` = `PendingCount` |
| 2 | Toolbox → Only continue if | Value > 0 |
| 3 | M365 Excel → Get table row | `Summary`, `Metric` = `PendingList` |
| 4 | Email by Postman | To ops lead. Subject "RC attendance NOT submitted (n)". Body: PendingList (no student data) |

## Pipe 3 — HR digest (3:05pm Mon–Fri)
| Step | App / action | Config |
|------|--------------|--------|
| Trigger | Scheduler → weekdays 15:05 | |
| 1 | M365 Excel → Get table row | `Summary`, `MissingCount` |
| 2 | Email by Postman | To HR. Subject "RC: n missing students". Body: count + workbook link only (D7: no names/phones in email) |

## Notes
- **[verify]** Excel recalculates formulas when Plumber reads via Graph. Test: submit a test response, wait 1 min, check Pipe 2/3 output matches the sheet.
- Do not let HR edit `Subs` (Plumber-owned). Corrections = add a new submission.
- Fallback if Plumber down: FormSG Results → download responses (secret key) → paste rows into `Subs` with the same columns.
