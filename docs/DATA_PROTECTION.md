# Data protection (MOE)

| # | Rule / risk | Control |
|---|-------------|---------|
| 1 | Real student/TDC data never leaves gov cloud | Only FormSG, Plumber, M365 Excel hold it. Repo + Netlify = code, templates, dummy data. `.gitignore` blocks xlsx/csv |
| 2 | **Checkbox options = student names visible to anyone with the form link** | DECIDED (D6): open link + verified MOE email (OTP). Singpass rejected (any Singpass holder can log in; collects NRIC); whitelist rejected (blocks relief teachers). Residual risk: names visible to link holders → link only in closed staff groups; rotate (duplicate form) if leaked |
| 3 | Minimum data | Name + school code + subject/class only. No NRIC, address, parent contact, medical |
| 4 | Email contains PII | DECIDED (D7): HR digest = count + link only. `Summary.MissingList` is for on-sheet use, never emailed |
| 5 | Access | Workbook shared to named HR/ops only (no "anyone with link"). FormSG/Plumber ≥2 admins |
| 6 | Secret key (FormSG Storage mode) | Approved vault; never chat/WhatsApp/repo |
| 7 | Retention | Archive & purge `Subs`/`CallLog` per school/MOE retention policy (confirm period) |
| 8 | Netlify toolkit | Static only, CSP `connect-src 'self'`, no forms/functions/analytics; files read via FileReader in-browser |
| 9 | AI tools | Never paste real roster/attendance into Claude or any AI. Use dummy data |
| 10 | Classification | Confirm with DPO / ICT (likely "Sensitive Normal") and record here |
