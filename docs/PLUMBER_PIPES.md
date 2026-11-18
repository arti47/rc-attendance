# Plumber pipes

Workbook: M365 Excel on gov cloud (Plumber connection). Tables: `Roster`, `Subs`, `Schedule`, `CallLog`, `Summary` (see EXCEL_WORKBOOK.md).
Click-by-click: PLUMBER_SETUP_GUIDE.md. **[verify]** = confirm in the Plumber UI on first build.

## Pipe 1: RC Absent intake (FormSG "RC Absent" → `Subs`)
| Step | Action | Config |
|------|--------|--------|
| Trigger | FormSG → New form response | Form "RC Absent" |
| 1 | Formatter → Date/time → Format **[verify]** | submission time → `yyyy-MM-dd`, Asia/Singapore |
| 2 | M365 Excel → Create table row → `Subs` | `SubmittedAt` = submission time; `Date` = step 1; `Type` = **`Absent`** (typed constant); `CentreClass` = Centre / Class; `Subject` = Subject; `Students` = all checkbox variables back-to-back; `Reason` = blank; `SubmissionID` = response ID; `SubmittedBy` = Staff email |

## Pipe 2: RC Late intake (FormSG "RC Late" → `Subs`)
Duplicate Pipe 1, change the trigger to form "RC Late", then remap:
`Type` = **`Late`**; `CentreClass` = Centre (e.g. `Mon | Geylang Methodist School`); `Subject` = blank; `Students` = all late checkbox variables back-to-back; `Reason` = Reason for lateness; the rest as Pipe 1.

## Pipe 3: HR digest (3:05pm Mon–Fri)
| Step | Action | Config |
|------|--------|--------|
| Trigger | Scheduler → weekdays 15:05 **[verify]** | |
| 1 | M365 Excel → Get table row | `Summary`, `Metric` = `MissingCount` |
| 2 | Email by Postman | To HR. Subject "RC: n missing students". Body: count + workbook link only (D7) |

No 2:55 chaser (D9): the +1 at each centre covers it on the ground.

## Notes
- **[verify]** Excel recalculates when Plumber reads via Graph. Test that Pipe 3's count matches the sheet.
- `Subs` is written by Plumber only. To correct something, submit again (latest wins for LateReason; absent ticks add up).
- If the date step is unavailable: write the raw timestamp to `Date`; formulas use `TEXT(Subs[Date],"yyyy-mm-dd")`. Check the timezone is SGT.
- Fallback if Plumber is down: FormSG → Results → download (secret key) → paste rows into `Subs` with the same columns; set `Type` by form.
