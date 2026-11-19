"""Build templates/RC_Attendance_Template.xlsx (structure + DUMMY data only).

Formulas are NOT written into cells (openpyxl cannot reliably emit dynamic-array /
structured-reference formulas). They are listed on the 'Formulas' sheet and in
docs/EXCEL_WORKBOOK.md for paste into Excel for the web. Keep both in sync: FORMULAS
below is the source of truth.

Usage: python3 scripts/build_workbook.py
"""
import csv
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "templates" / "RC_Attendance_Template.xlsx"

T = 'TEXT(TODAY(),"yyyy-mm-dd")'
D = 'TEXT(TODAY(),"dddd")'
IN_LIST = 'ISNUMBER(FIND(","&[@Key]&",",","&SUBSTITUTE(Subs[Students],", ",",")&","))'


def scoped(kind):
    # Absent: teacher form, scoped to the student's Centre/Class + Subject.
    # Late: +1 officer form, centre-wide (Subs.CentreClass = "Ddd | Centre", Subject blank);
    #       key is globally unique (toolkit enforces), so match on date + key only.
    base = f'(TEXT(Subs[Date],"yyyy-mm-dd")={T})*(Subs[Type]="{kind}")'
    if kind == "Absent":
        base += '*(Subs[CentreClass]=[@CentreClass])*(Subs[Subject]=[@Subject])'
    return f'{base}*{IN_LIST}'


# (sheet/table, column) -> formula. Order matters (dependencies left to right).
FORMULAS = [
    ("Roster", "Key", '=TRIM([@StudentName])&" ("&UPPER(TRIM([@SchoolCode]))&") "&UPPER([@Subject])&[@Class]'),
    ("Roster", "CentreClass", '=LEFT([@Day],3)&" | "&TRIM([@Centre])&" | C"&[@Class]'),
    ("Roster", "AbsentToday", f'=IF([@Day]<>{D},0,SUMPRODUCT({scoped("Absent")}))'),
    ("Roster", "LateToday", f'=IF([@Day]<>{D},0,SUMPRODUCT({scoped("Late")}))'),
    ("Roster", "Status", '=IF([@AbsentToday]>0,IF([@LateToday]>0,"ARRIVED LATE","MISSING"),IF([@LateToday]>0,"LATE (not flagged)",""))'),
    ("Roster", "FlaggedAt", f'=IF([@AbsentToday]=0,"",LOOKUP(2,1/({scoped("Absent")}),Subs[SubmittedAt]))'),
    ("Roster", "LateReason", f'=IF([@LateToday]=0,"",LOOKUP(2,1/({scoped("Late")}),Subs[Reason]))'),
    ("Roster", "HROutcome", f'=IF([@Status]="","",IFERROR(LOOKUP(2,1/((TEXT(CallLog[Date],"yyyy-mm-dd")={T})*(CallLog[StudentKey]=[@Key])),CallLog[Outcome]),""))'),
    ("Schedule", "Submitted", f'=IF([@Day]<>{D},"",IF(SUMPRODUCT((TEXT(Subs[Date],"yyyy-mm-dd")={T})*(Subs[Type]="Absent")*(Subs[CentreClass]=[@CentreClass])*(Subs[Subject]=[@Subject]))>0,"Yes","PENDING"))'),
    ("Summary", "Value (PendingCount)", '=COUNTIF(Schedule[Submitted],"PENDING")'),
    ("Summary", "Value (PendingList)", '=IF(COUNTIF(Schedule[Submitted],"PENDING")=0,"None",TEXTJOIN(CHAR(10),TRUE,FILTER(Schedule[CentreClass]&" | "&Schedule[Subject],Schedule[Submitted]="PENDING")))'),
    ("Summary", "Value (MissingCount)", '=COUNTIF(Roster[Status],"MISSING")'),
    ("Summary", "Value (ArrivedLateCount)", '=COUNTIF(Roster[Status],"ARRIVED LATE")'),
    ("Summary", "Value (UnresolvedCount)", '=SUMPRODUCT((Roster[Status]="MISSING")*NOT(ISNUMBER(MATCH(Roster[HROutcome],{"Located - at home school","Located - at home","Absent - valid reason (MC/leave)"},0))))'),
    ("Summary", "Value (MissingList)", '=IF(COUNTIF(Roster[Status],"MISSING")=0,"None",TEXTJOIN(CHAR(10),TRUE,FILTER(Roster[StudentName]&" | "&Roster[HomeSchool]&" | TDC "&Roster[TDCName]&" "&Roster[TDCPhone]&" | "&Roster[CentreClass]&" "&Roster[Subject],Roster[Status]="MISSING")))'),
    ("HR View", "A2 (spill)", '=IFERROR(SORT(FILTER(HSTACK(Roster[Status],Roster[FlaggedAt],Roster[StudentName],Roster[HomeSchool],Roster[TDCName],Roster[TDCPhone],Roster[CentreClass],Roster[Subject],Roster[LateReason],Roster[HROutcome],Roster[Key]),Roster[Status]<>""),{1,2},{-1,1}),"No absentees reported yet")'),
]

# CallLog.Outcome dropdown (D12). Also used by Summary UnresolvedCount — keep in sync.
OUTCOMES = [
    "Located - at home school",
    "Located - at home",
    "Absent - valid reason (MC/leave)",
    "No answer - retry",
    "Not located - escalated",
]

TABLES = {
    "Roster": ["StudentName", "HomeSchool", "SchoolCode", "Day", "Centre", "Class", "Subject", "TDCName", "TDCPhone",
               "Key", "CentreClass", "AbsentToday", "LateToday", "Status", "FlaggedAt", "LateReason", "HROutcome"],
    "Subs": ["SubmittedAt", "Date", "Type", "CentreClass", "Subject", "Students", "Reason", "SubmissionID", "SubmittedBy"],
    "Schedule": ["Day", "CentreClass", "Subject", "Submitted"],
    "CallLog": ["Date", "StudentKey", "Outcome", "CalledBy", "Notes"],
    "Summary": ["Metric", "Value"],
}
HR_HEADERS = ["Status", "FlaggedAt", "Student", "Home school", "TDC", "TDC phone", "Centre/Class", "Subj",
              "Late reason", "HR outcome", "Key (copy to CallLog)"]
HEAD = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="1F4E8C")


def read_csv(p):
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def add_table(wb, name, headers, rows):
    ws = wb.create_sheet(name)
    ws.append(headers)
    for r in rows:
        ws.append([r.get(h, "") for h in headers])
    end_row = max(2, len(rows) + 1)
    if not rows:
        ws.append([""] * len(headers))
    ref = f"A1:{ws.cell(row=1, column=len(headers)).column_letter}{end_row}"
    t = Table(displayName=name, ref=ref)
    t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    ws.add_table(t)
    for c in ws[1]:
        c.font = HEAD
        c.fill = FILL
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 18
    return ws


def main():
    schedule = read_csv(ROOT / "data" / "schedule.csv")
    roster = read_csv(ROOT / "templates" / "roster_template.csv")
    wb = Workbook()
    wb.remove(wb.active)

    hr = wb.create_sheet("HR View")
    for i, h in enumerate(HR_HEADERS, 1):
        c = hr.cell(row=1, column=i, value=h)
        c.font, c.fill = HEAD, FILL
        hr.column_dimensions[c.column_letter].width = 20
    hr["M1"] = "Paste 'HR View A2 (spill)' formula into A2. Read-only. Record call outcomes in CallLog."

    add_table(wb, "Roster", TABLES["Roster"], roster)
    subs = add_table(wb, "Subs", TABLES["Subs"], [])
    for col in ("A", "B"):
        subs[f"{col}2"].number_format = "@"  # keep Plumber-written dates as text
    sched_rows = [{"Day": s["Day"], "CentreClass": f'{s["Day"][:3]} | {s["Centre"]} | C{s["Class"]}', "Subject": sub}
                  for s in schedule for sub in "EMS"]
    add_table(wb, "Schedule", TABLES["Schedule"], sched_rows)
    cl = add_table(wb, "CallLog", TABLES["CallLog"], [])
    dv = DataValidation(type="list", formula1='"' + ",".join(OUTCOMES) + '"', allow_blank=True,
                        showErrorMessage=True, errorTitle="Outcome", error="Pick from the list")
    cl.add_data_validation(dv)
    dv.add("C2:C5000")
    add_table(wb, "Summary", TABLES["Summary"],
              [{"Metric": m} for m in ["PendingCount", "PendingList", "MissingCount", "ArrivedLateCount", "UnresolvedCount", "MissingList"]])

    fs = wb.create_sheet("Formulas")
    fs.append(["Sheet/Table", "Column / Cell", "Formula (paste into first data cell; table auto-fills column)"])
    for i, (sheet, col, f) in enumerate(FORMULAS, start=2):
        fs.cell(row=i, column=1, value=sheet)
        fs.cell(row=i, column=2, value=col)
        c = fs.cell(row=i, column=3)
        c.value = f
        c.data_type = "s"     # store as TEXT, not a live formula (else Excel shows #REF!)
        c.quotePrefix = True  # Excel shows it as typed text; copying gives the plain formula
    fs.column_dimensions["A"].width = 12
    fs.column_dimensions["B"].width = 26
    fs.column_dimensions["C"].width = 160

    OUT.parent.mkdir(exist_ok=True)
    wb.save(OUT)
    print(f"wrote {OUT.relative_to(ROOT)}")

    md = ["# Excel formulas (AUTO-GENERATED by scripts/build_workbook.py — do not edit by hand)", "",
          "Paste each into the FIRST data row of the column; Excel tables auto-fill the whole column.", ""]
    for sheet, col, f in FORMULAS:
        md += [f"## {sheet} → {col}", "", "```", f, "```", ""]
    (ROOT / "docs" / "excel_formulas.md").write_text("\n".join(md), encoding="utf-8")
    print("wrote docs/excel_formulas.md")
    write_office_script()


def write_office_script():
    """Office Script (Excel for the web → Automate) that installs every formula in one run."""
    rows = ",\n".join(f"    [{json.dumps(s)}, {json.dumps(c)}, {json.dumps(f)}]" for s, c, f in FORMULAS)
    ts = OFFICE_SCRIPT.replace("__ROWS__", rows)
    out = ROOT / "scripts" / "office" / "SetupFormulas.ts"
    out.parent.mkdir(exist_ok=True)
    out.write_text(ts, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


OFFICE_SCRIPT = """// AUTO-GENERATED by scripts/build_workbook.py — do not edit by hand.
// Excel for the web → Automate → New Script → paste all of this → Save → Run.
// Safe to run again (it just rewrites the same formulas).
function main(workbook: ExcelScript.Workbook) {
  const F: string[][] = [
__ROWS__
  ];
  const problems: string[] = [];
  for (const [sheet, col, formula] of F) {
    if (sheet === "HR View") {
      const ws = workbook.getWorksheet("HR View");
      if (!ws) { problems.push("Sheet 'HR View' not found"); continue; }
      ws.getRange("A2").setFormula(formula);
    } else if (sheet === "Summary") {
      const m = col.match(/\\((.+)\\)/);
      const t = workbook.getTable("Summary");
      if (!m || !t) { problems.push("Summary table or metric missing: " + col); continue; }
      const mc = t.getColumnByName("Metric");
      const vc = t.getColumnByName("Value");
      if (!mc || !vc) { problems.push("Summary needs Metric and Value columns"); continue; }
      const i = mc.getRangeBetweenHeaderAndTotal().getValues().findIndex((r) => r[0] === m[1]);
      if (i < 0) { problems.push("Summary row missing: " + m[1]); continue; }
      vc.getRangeBetweenHeaderAndTotal().getCell(i, 0).setFormula(formula);
    } else {
      const t = workbook.getTable(sheet);
      const c = t ? t.getColumnByName(col) : undefined;
      if (!c) { problems.push("Column not found: " + sheet + "[" + col + "]"); continue; }
      c.getRangeBetweenHeaderAndTotal().setFormula(formula);
    }
  }
  // Report any formula errors (#NAME?, #REF!, ...)
  for (const name of ["Roster", "Schedule", "Summary"]) {
    const t = workbook.getTable(name);
    if (!t) continue;
    const head = t.getHeaderRowRange().getValues()[0];
    t.getRangeBetweenHeaderAndTotal().getValues().forEach((row, r) =>
      row.forEach((v, c) => {
        if (typeof v === "string" && v.startsWith("#")) problems.push(name + " row " + (r + 2) + " " + head[c] + ": " + v);
      }));
  }
  const hr = workbook.getWorksheet("HR View");
  const a2 = hr ? String(hr.getRange("A2").getValue()) : "";
  if (a2.startsWith("#")) problems.push("HR View A2: " + a2);
  console.log(problems.length ? "PROBLEMS:\\n" + problems.join("\\n") : "OK - all " + F.length + " formulas installed, no errors.");
}
"""


if __name__ == "__main__":
    main()
