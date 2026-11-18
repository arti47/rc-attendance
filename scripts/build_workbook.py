"""Build templates/RC_Attendance_Template.xlsx (structure + DUMMY data only).

Formulas are NOT written into cells (openpyxl cannot reliably emit dynamic-array /
structured-reference formulas). They are listed on the 'Formulas' sheet and in
docs/EXCEL_WORKBOOK.md for paste into Excel for the web. Keep both in sync: FORMULAS
below is the source of truth.

Usage: python3 scripts/build_workbook.py
"""
import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "templates" / "RC_Attendance_Template.xlsx"

T = 'TEXT(TODAY(),"yyyy-mm-dd")'
D = 'TEXT(TODAY(),"dddd")'
IN_LIST = 'ISNUMBER(FIND(","&[@Key]&",",","&SUBSTITUTE(Subs[Students],", ",",")&","))'


def scoped(kind):
    return (f'(TEXT(Subs[Date],"yyyy-mm-dd")={T})*(Subs[Type]="{kind}")'
            f'*(Subs[CentreClass]=[@CentreClass])*(Subs[Subject]=[@Subject])*{IN_LIST}')


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
    ("Summary", "Value (MissingList)", '=IF(COUNTIF(Roster[Status],"MISSING")=0,"None",TEXTJOIN(CHAR(10),TRUE,FILTER(Roster[StudentName]&" | "&Roster[HomeSchool]&" | TDC "&Roster[TDCName]&" "&Roster[TDCPhone]&" | "&Roster[CentreClass]&" "&Roster[Subject],Roster[Status]="MISSING")))'),
    ("HR View", "A2 (spill)", '=IFERROR(SORT(FILTER(HSTACK(Roster[Status],Roster[FlaggedAt],Roster[StudentName],Roster[HomeSchool],Roster[TDCName],Roster[TDCPhone],Roster[CentreClass],Roster[Subject],Roster[LateReason],Roster[HROutcome],Roster[Key]),Roster[Status]<>""),{1,2},{-1,1}),"No absentees reported yet")'),
]

TABLES = {
    "Roster": ["StudentName", "HomeSchool", "SchoolCode", "Day", "Centre", "Class", "Subject", "TDCName", "TDCPhone",
               "Key", "CentreClass", "AbsentToday", "LateToday", "Status", "FlaggedAt", "LateReason", "HROutcome"],
    "Subs": ["SubmittedAt", "Date", "Type", "CentreClass", "Subject", "Students", "Reason", "SubmissionID"],
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
    add_table(wb, "CallLog", TABLES["CallLog"], [])
    add_table(wb, "Summary", TABLES["Summary"],
              [{"Metric": m} for m in ["PendingCount", "PendingList", "MissingCount", "ArrivedLateCount", "MissingList"]])

    fs = wb.create_sheet("Formulas")
    fs.append(["Sheet/Table", "Column / Cell", "Formula (paste into first data cell; table auto-fills column)"])
    for row in FORMULAS:
        fs.append(list(row))
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


if __name__ == "__main__":
    main()
