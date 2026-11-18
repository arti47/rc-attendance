# FormSG spec: "RC Attendance" (single form)

**Mode:** Storage mode (required for Plumber). Secret key → approved vault, never chat/repo/email.
**Collaborators:** ≥2 admins.

## Fields (in order)
| # | Field | Type | Required | Options / notes |
|---|-------|------|----------|-----------------|
| 1 | Centre / Class | Dropdown | Yes | Paste from toolkit "Centre/Class options", e.g. `Mon \| Geylang Methodist School \| C2` |
| 2 | Subject | Radio | Yes | `E`, `M`, `S` (exact values — Excel matches on them) |
| 3 | Report type | Radio | Yes | `Absent`, `Late` (exact values) |
| 4..N | `<Day \| Centre \| Class \| Subj>` | Checkbox | Yes | One field per Centre/Class/Subject group. First option `NONE - all present`, then student keys from toolkit. "Others" OFF |
| N+1 | Reason for lateness | Paragraph | Yes (when shown) | Free text, e.g. "Alex – bus delay; Bella – dentist" |

## Logic
- Each checkbox field: **Show** when `Centre / Class` = its centre-class **AND** `Subject` = its subject.
- Reason field: **Show** when `Report type` = `Late`.
- Same checkbox list used for Absent and Late (late = tick who arrived late).

Count: centre-classes × 3 checkbox fields (20 × 3 = 60 with current schedule). One-time setup; roster changes only edit options (copy from toolkit).

## Teacher flow (target < 40 s)
Open pinned link → Centre/Class → Subject → Absent → tick (or NONE) → Submit.
At 3:00: same link → … → Late → tick → reason → Submit.

## Rules
- Never add NRIC, address, parent contact or medical info.
- Student option text must equal Roster `Key` exactly. Always regenerate from the toolkit.
- Must submit even if all present (`NONE`) — that's how the chaser knows.
