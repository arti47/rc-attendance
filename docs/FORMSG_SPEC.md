# FormSG spec: two forms

| Form | Who | When | Link shared in |
|------|-----|------|----------------|
| **RC Absent** | Subject teacher (E/M/S), after collecting their students | by 2:50pm | Teacher staff group |
| **RC Late** | "+1" at each centre (GEB officer or centre head), walks round the centre | ~3:00pm | +1 group |

Both forms use **Storage mode** (required for Plumber). Store each secret key in the approved vault, never in chat, the repo or email. Each form has ≥2 admins.
Both are open links with staff email verification (D6). Student names in the options are visible to anyone with the link, so share links only in closed staff groups. If a link leaks, duplicate the form to get a new link and re-point the Plumber trigger.

## Form 1: RC Absent
| # | Field | Type | Req | Options / notes |
|---|-------|------|-----|-----------------|
| 1 | Staff email | Email, **Verify ON** | Yes | Allowed domains `moe.edu.sg`, `schools.gov.sg` (+ others relief staff use) |
| 2 | Centre / Class | Dropdown | Yes | Toolkit "ABSENT form: Centre / Class options", e.g. `Mon \| Geylang Methodist School \| C2` |
| 3 | Subject | Radio | Yes | `E`, `M`, `S` (exact) |
| 4..N | `<Ddd \| Centre \| C<n> \| Subj>` | Checkbox | Yes | One per Centre/Class/Subject (20×3 = 60). First option `NONE - all present`, then student keys. "Others" OFF |

Logic: each checkbox field is shown when `Centre / Class` = its centre-class **AND** `Subject` = its subject.
Teacher flow (~40 s): link → email + code → Centre/Class → Subject → tick absentees (or NONE) → Submit.
`NONE` is mandatory when all are present, so the sheet can show which groups haven't reported.

## Form 2: RC Late
| # | Field | Type | Req | Options / notes |
|---|-------|------|-----|-----------------|
| 1 | Staff email | Email, **Verify ON** | Yes | Same domains |
| 2 | Centre | Dropdown | Yes | Toolkit "LATE form: Centre options", e.g. `Mon \| Geylang Methodist School` |
| 3..M | `<Ddd \| Centre>` | Checkbox | Yes | One per centre-day (15 now). All the centre's students (all classes and subjects), sorted by name; first option `NONE - all present` |
| M+1 | Reason for lateness | Paragraph | Yes | e.g. "Alex Tan – bus delay; Bella Lim – dentist". For the internal log and TDC feedback |

Logic: each checkbox field is shown when `Centre` = its title.
Flow: link → email + code → Centre → tick latecomers → reasons → Submit. One submission per centre.
Effect: a ticked student flagged absent at 2:50 becomes `ARRIVED LATE`. A ticked student not flagged becomes `LATE (not flagged)`, which is feedback for the teacher.

## Rules
- Never add NRIC, address, parent contact or medical info.
- Option text must equal the Roster `Key` exactly. Always copy it from the toolkit.
- Roster change → update options in **both** forms.
