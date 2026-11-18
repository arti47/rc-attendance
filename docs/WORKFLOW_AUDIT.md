# Workflow audit: current vs proposed

## Current workflow (as described)
```
2:50pm teacher -> FormSG (1 form per centre, tick absentees)
       -> Plumber -> Excel (names only)
       -> HR manually looks up home school + TDC + phone   <-- bottleneck
3:00pm teacher -> FormSG latecomers -> checked off original list
3:10pm HR starts calling schools
```

## Findings
| # | Issue | Impact | Fix |
|---|-------|--------|-----|
| 1 | Lookup of school/TDC/phone is manual | Main delay before 3:10; error-prone | Master **Roster** table; formulas auto-fill school/TDC/phone the instant Plumber writes a row |
| 2 | No way to tell "no absentees" from "teacher forgot to submit" | Silent gaps | Mandatory `NONE - all present` option; Schedule sheet shows groups not yet reported. Chasing is done in person by the centre +1 (no chaser email, D9) |
| 3 | One form per centre = many links + many Plumber pipes | Teachers lose links; each roster change touches many forms/pipes | **Two forms total**: one Absent (teachers), one Late (+1s). One link per role, pinned in the staff group |
| 4 | Free typing / school selection by teacher | Slow, typos break lookups | Teacher only taps: Centre/Class → Subject → tick names. Key = `Name (SCHOOLCODE) SubjectClass` |
| 5 | Late reconciliation by hand | HR may call for a child who already arrived | Late submission auto-flips status to `ARRIVED LATE`; late reason logged for TDC feedback |
| 6 | Plumber per-student loops / lookups | Fragile, uses more Plumber steps | Plumber writes **one row per submission**; Excel does the explode/lookup. Pipe has 1–2 steps |
| 7 | Student data on multiple surfaces | MOE data-protection risk | Data stays in gov-cloud FormSG + Plumber + M365 Excel. Netlify toolkit is client-side only, no storage |
| 8 | Bus factor | Pipe/form owned by one officer | Add ≥2 collaborators on FormSG + Plumber; secret key in approved vault |

## Proposed timeline
| Time | Event | Actor |
|------|-------|-------|
| by 2:50 | Absent submission after collecting students (~40 s) | Subject teacher (E/M/S each) |
| ~2:50:30 | Row in `Subs`; HR View shows MISSING + school + TDC + phone | Plumber + Excel (auto) |
| ~3:00 | +1 walks the centre, one Late submission per centre + reasons → ARRIVED LATE | +1 (GEB officer / centre head) |
| 3:05 | HR email: missing count + link | Plumber scheduler |
| 3:05–3:10 | HR calls TDCs, logs outcome in `CallLog` | HR |

Net: data ready ~2:51 instead of "by 3:10"; zero manual lookup.

## Open recommendations (need your decision)
