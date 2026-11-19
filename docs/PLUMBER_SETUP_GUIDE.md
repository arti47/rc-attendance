# Plumber setup: step by step

Do these steps on a work device only. Plumber's menu names change over time; if a label doesn't match, use the nearest option or check guide.plumber.gov.sg, or send Claude a screenshot.
Before you start: the Excel workbook is built (EXCEL_WORKBOOK.md) and both FormSG forms are built (FORMSG_SPEC.md) in **Storage mode**.

Build order: **A → B → test → C → test → D → E**.

---

## Part A: Connect Excel (once)
1. Go to **plumber.gov.sg** and log in with your gov email + one-time code.
2. Left menu → **Connections** (or "Apps") → **M365 Excel** → **Connect**.
3. Follow the prompt. Plumber only reads and writes files in the gov SharePoint location it names.
   - If Plumber asks you to create the file from inside Plumber, do that, then open it in Excel for the web and recreate the 5 tables (Roster, Subs, Schedule, CallLog, Summary) with the template's headers.
   - The tables must be real Excel **Tables** (Insert → Table), not just ranges.
4. Share the workbook with HR and centre heads by name. Do not use "Anyone with the link".

## Part B: Pipe 1, "RC Absent intake"
1. **Pipes → Create pipe** → name it `RC Absent intake`.
2. **Trigger** → **FormSG** → **New form response**.
3. Paste the **RC Absent** form URL (and the secret key, if asked) into Plumber only.
   - If Plumber shows a **webhook URL** instead: FormSG → form → **Settings → Webhooks** → paste it → Save.
4. Submit **one test response** with fake data (tick `NONE - all present`).
5. In Plumber click **Check step** / **Test**. The test answers appear and the form fields become available to map.
6. **Add step → Formatter → Date & time → Format date**: input submission time, format `yyyy-MM-dd`, timezone `Asia/Singapore`. If this action doesn't exist, skip this step.
7. **Add step → M365 Excel → Create table row** → your workbook → table `Subs`:

   | Excel column | Value |
   |---|---|
   | SubmittedAt | Submission time |
   | Date | Step 6 output (or submission time) |
   | Type | type the word `Absent` |
   | CentreClass | "Centre / Class" answer |
   | Subject | "Subject" answer |
   | Students | **all checkbox-field variables back to back, nothing between them** (only one has a value per submission) |
   | Reason | type `-` (Plumber rejects empty boxes) |
   | SubmissionID | Response ID |
   | SubmittedBy | "Staff email" answer |
8. **Test step** → check that a new row appears in `Subs`.
9. **Publish**.
10. Check the result: add a fake Roster row with today's Day, submit an absent tick for it → Status = `MISSING` and the student shows on HR View.

## Part C: Pipe 2, "RC Late intake"
1. On Pipe 1 → **⋯ → Duplicate** (if you can't duplicate, repeat Part B). Rename it `RC Late intake`.
2. Change the trigger form to **RC Late**, then send a test response and run **Check step**.
3. Delete the Formatter step if it errors and re-add it. Remap step 7:
   - Type → `Late`
   - CentreClass → "Centre" answer
   - Subject → type `-`
   - Students → all **late** checkbox variables back to back
   - Reason → "Reason for lateness"
   - SubmittedBy → "Staff email"
4. Test with the fake student from Part B step 10 → Status becomes `ARRIVED LATE` and the reason shows. Publish.

## Part D: Pipe 3, "RC HR digest" (3:05pm)
1. **Create pipe** → `RC HR digest`.
2. **Trigger → Scheduler** → weekly, **Mon, Tue, Wed, Thu** at **15:05**.
3. **M365 Excel → Get table row** → `Summary`, lookup column `Metric`, value `MissingCount`.
4. **Email by Postman** → To: HR group email. Subject `RC: <MissingCount> missing students`. Body: `Open HR View: <workbook link>`. **No names or phone numbers.**
5. Test, then publish. Delete all test rows from `Subs` and `Roster`.

## Part E: Hand-over safety
1. Each pipe → **Collaborators** → add a 2nd admin.
2. Each form → **Settings → Collaborators** → add a 2nd admin.
3. Put both FormSG secret keys in the approved vault.

## If something breaks
| Symptom | Check |
|---|---|
| No row in `Subs` | Pipe published? Webhook saved in FormSG? Plumber → pipe → **Executions** shows the error |
| Row appears but Status blank | Roster `Day` ≠ today, or option text ≠ Roster `Key` (re-copy options from the toolkit) |
| Late tick not flipping status | `Type` must be exactly `Late`; student key must match the Absent form's key |
| HR email count wrong | Excel didn't recalculate before Plumber read it. Open the workbook, re-run the pipe; tell Claude if it repeats |
| Plumber down | FormSG → Results → download (secret key) → paste into `Subs` |
