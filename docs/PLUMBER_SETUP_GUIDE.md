# Plumber setup: step by step

Do these steps on a work device only. Plumber's menu names change over time; if a label doesn't match, use the nearest option and see guide.plumber.gov.sg.
Before you start: the Excel workbook is built (EXCEL_WORKBOOK.md) and the FormSG form is built (FORMSG_SPEC.md) in **Storage mode**.

---

## Part A: Connect Excel (once)
1. Go to **plumber.gov.sg** and log in with your gov email + one-time code.
2. Left menu → **Connections** (or "Apps") → **M365 Excel** → **Connect**.
3. Follow the prompt. Plumber only reads and writes files in the gov SharePoint location it names.
   - If Plumber asks you to create the file from inside Plumber, do that, then open it in Excel for the web and recreate the 5 tables (Roster, Subs, Schedule, CallLog, Summary) with the template's headers.
   - The tables must be real Excel **Tables** (Insert → Table), not just ranges, or Plumber can't see them.
4. Share the workbook with HR and ops by name. Do not use "Anyone with the link".

## Part B: Pipe 1, "RC Attendance Intake" (FormSG → Excel)
1. **Pipes → Create pipe** → name it `RC Attendance Intake`.
2. **Trigger** → choose **FormSG** → event **New form response**.
3. Plumber asks for the **form URL** (and the **secret key** in some versions). Paste them into Plumber only.
   - If Plumber shows a **webhook URL** instead: FormSG → your form → **Settings → Webhooks** → paste it → Save.
4. Submit **one test response** in FormSG with fake data: any Centre/Class, Subject `M`, Report type `Absent`, tick `NONE - all present`.
5. Back in Plumber, click **Check step** or **Test**. You should see the test answers. This makes the form fields available to map in the next steps.
6. **Add step → Formatter → Date & time → Format date**. If this action doesn't exist, skip to step 7.
   - Input: submission time. Format: `yyyy-MM-dd`. Timezone: `Asia/Singapore`.
7. **Add step → M365 Excel → Create table row**.
   - File: your workbook. Table: `Subs`.
   - Map each column (click the field, then pick a variable from the trigger):

   | Excel column | Value |
   |---|---|
   | SubmittedAt | Submission time |
   | Date | Output of step 6 (or submission time if step 6 was skipped) |
   | Type | "Report type" answer |
   | CentreClass | "Centre / Class" answer |
   | Subject | "Subject" answer |
   | Students | **Insert ALL checkbox-field variables one after another, with nothing between them**. Only one has a value per submission, so the result is that group's ticks |
   | Reason | "Reason for lateness" answer |
   | SubmissionID | Response ID |
   | SubmittedBy | "Staff email" answer |
8. Click **Test step**. Open Excel and check that a new row appears in `Subs`.
9. **Publish** the pipe (top right).
10. Check the result: put a fake Roster row with today's Day in Excel, submit an Absent tick for that student → Roster Status = `MISSING` and the student shows on HR View. Submit a Late tick → `ARRIVED LATE`. Delete all test rows.

> Tip: setting up step 7 is tedious with 60 checkbox fields. Do the mapping once, test it, then never touch it. A roster change only edits the options *inside* fields; you only re-map when you **add a new centre/class** (new checkbox fields).

## Part C: Pipe 2, "RC Not-submitted chaser" (2:55pm)
1. **Create pipe** → `RC Not-submitted chaser`.
2. **Trigger → Scheduler** → **Weekly**: Mon–Fri (only the days classes run) at **14:55**.
3. **Add step → M365 Excel → Get table row** → table `Summary`, lookup column `Metric`, value `PendingCount`.
4. **Add step → Toolbox → Only continue if** → `Value` (from step 3) **greater than** `0`.
5. **Add step → M365 Excel → Get table row** → `Summary`, `Metric` = `PendingList`.
6. **Add step → Email by Postman → Send email**.
   - To: **Centre head** (D8). Add a backup person in CC for leave cover
   - Subject: `RC attendance NOT submitted: <PendingCount> group(s)`
   - Body: `Not yet submitted:` then a new line, then `<PendingList value>`. Add the workbook link.
7. Test. Temporarily set a Schedule row's Day to today with no submission → the email should arrive.
8. Publish.

## Part D: Pipe 3, "RC HR digest" (3:05pm)
1. **Create pipe** → `RC HR digest`.
2. **Trigger → Scheduler** → Mon–Fri **15:05**.
3. **M365 Excel → Get table row** → `Summary`, `Metric` = `MissingCount`.
4. **Email by Postman** → To: HR group email. Subject `RC: <MissingCount> missing students`. Body: `Open the HR View: <workbook link>`. **No names or phone numbers in the email.**
5. Test, then publish.

## Part E: Hand-over safety
1. Each pipe → **Settings / Collaborators** → add a 2nd admin.
2. FormSG → **Settings → Collaborators** → add a 2nd admin.
3. Store the FormSG secret key in your approved vault.

## If something breaks
| Symptom | Check |
|---|---|
| No row in `Subs` | Pipe 1 published? Webhook URL saved in FormSG? Plumber → pipe → **Executions** shows the error |
| Row appears but Status blank | Roster `Day` ≠ today's weekday, or option text ≠ Roster `Key` (regenerate options with the toolkit) |
| Emails show old numbers | Excel didn't recalculate before Plumber read it. Open the workbook once, then re-run the pipe. If it keeps happening, tell Claude |
| Plumber down at 2:50 | FormSG → Results → download CSV (secret key) → paste rows into `Subs` |
