// Pure logic shared by the browser toolkit and node tests. No network, no storage.
// Key format MUST stay identical to the Excel formula in docs/EXCEL_WORKBOOK.md:
//   =TRIM([@StudentName])&" ("&TRIM([@SchoolCode])&") "&[@Subject]&[@Class]
// e.g. "Alex Tan Wei Ming (DPS) M1"

export const SUBJECTS = ['E', 'M', 'S'];
export const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
export const ROSTER_COLS = ['StudentName', 'HomeSchool', 'SchoolCode', 'Day', 'Centre', 'Class', 'Subject', 'TDCName', 'TDCPhone'];
export const NONE_OPTION = 'NONE - all present';

const clean = (s) => String(s ?? '').replace(/\s+/g, ' ').trim();

export function parseCSV(text) {
  const rows = [];
  let row = [], field = '', q = false;
  text = String(text).replace(/^﻿/, '');
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') q = false;
      else field += c;
    } else if (c === '"') q = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(field); field = '';
      if (row.some((f) => f.trim() !== '')) rows.push(row);
      row = [];
    } else field += c;
  }
  row.push(field);
  if (row.some((f) => f.trim() !== '')) rows.push(row);
  if (!rows.length) return [];
  const head = rows[0].map(clean);
  return rows.slice(1).map((r) => Object.fromEntries(head.map((h, i) => [h, clean(r[i])])));
}

export function studentKey(r) {
  return `${clean(r.StudentName)} (${clean(r.SchoolCode).toUpperCase()}) ${clean(r.Subject).toUpperCase()}${clean(r.Class)}`;
}

export function centreClassLabel(day, centre, cls) {
  return `${clean(day).slice(0, 3)} | ${clean(centre)} | C${clean(cls)}`;
}

export function centreLabel(day, centre) {
  return `${clean(day).slice(0, 3)} | ${clean(centre)}`;
}

export function groupLabel(day, centre, cls, subject) {
  return `${centreClassLabel(day, centre, cls)} | ${clean(subject).toUpperCase()}`;
}

const PHONE = /^[689]\d{7}$/;

export function validate(roster, schedule = []) {
  const errors = [], warnings = [];
  if (!roster.length) errors.push('Roster is empty.');
  const missingCols = ROSTER_COLS.filter((c) => roster.length && !(c in roster[0]));
  if (missingCols.length) errors.push(`Missing columns: ${missingCols.join(', ')}`);
  const sched = new Set(schedule.map((s) => centreClassLabel(s.Day, s.Centre, s.Class)));
  const seen = new Map();
  roster.forEach((r, i) => {
    const line = i + 2;
    for (const c of ROSTER_COLS) if (!clean(r[c])) errors.push(`Row ${line}: ${c} is blank.`);
    if (r.Subject && !SUBJECTS.includes(clean(r.Subject).toUpperCase())) errors.push(`Row ${line}: Subject must be E, M or S.`);
    if (r.Day && !DAYS.includes(clean(r.Day))) errors.push(`Row ${line}: Day "${r.Day}" invalid (use full day name).`);
    if (/[,*?~]/.test(r.StudentName || '')) errors.push(`Row ${line}: StudentName has , * ? or ~ (breaks FormSG/Excel matching).`);
    const phone = clean(r.TDCPhone).replace(/[\s+-]/g, '').replace(/^65(?=\d{8}$)/, '');
    if (r.TDCPhone && !PHONE.test(phone)) warnings.push(`Row ${line}: TDCPhone "${r.TDCPhone}" not an 8-digit SG number.`);
    if (schedule.length && r.Centre && !sched.has(centreClassLabel(r.Day, r.Centre, r.Class)))
      errors.push(`Row ${line}: ${centreClassLabel(r.Day, r.Centre, r.Class)} not in schedule.`);
    const k = studentKey(r);
    if (seen.has(k)) errors.push(`Row ${line}: duplicate key "${k}" (also row ${seen.get(k)}). Add middle name/initial.`);
    else seen.set(k, line);
  });
  // substring collisions break wildcard matching in Excel
  const keys = [...seen.keys()];
  for (const a of keys) for (const b of keys) if (a !== b && b.includes(a)) warnings.push(`Key "${a}" is contained in "${b}" — rename one.`);
  return { errors, warnings };
}

// One FormSG checkbox field per Centre/Class/Subject group.
export function formGroups(roster) {
  const g = new Map();
  for (const r of roster) {
    const label = groupLabel(r.Day, r.Centre, r.Class, r.Subject);
    if (!g.has(label)) g.set(label, { label, day: clean(r.Day), centreClass: centreClassLabel(r.Day, r.Centre, r.Class), subject: clean(r.Subject).toUpperCase(), options: [] });
    g.get(label).options.push(studentKey(r));
  }
  const order = (x) => DAYS.indexOf(x.day);
  return [...g.values()]
    .map((x) => ({ ...x, options: [NONE_OPTION, ...x.options.sort((a, b) => a.localeCompare(b))] }))
    .sort((a, b) => order(a) - order(b) || a.label.localeCompare(b.label));
}

// Late form (+1 officer): one checkbox field per centre-day, all students, sorted by name.
export function lateGroups(roster) {
  const g = new Map();
  for (const r of roster) {
    const label = centreLabel(r.Day, r.Centre);
    if (!g.has(label)) g.set(label, { label, day: clean(r.Day), options: [] });
    g.get(label).options.push(studentKey(r));
  }
  return [...g.values()]
    .map((x) => ({ ...x, options: [NONE_OPTION, ...x.options.sort((a, b) => a.localeCompare(b))] }))
    .sort((a, b) => DAYS.indexOf(a.day) - DAYS.indexOf(b.day) || a.label.localeCompare(b.label));
}

export function centreOptions(schedule) {
  return [...new Set(schedule.slice().sort((a, b) => DAYS.indexOf(a.Day) - DAYS.indexOf(b.Day)).map((s) => centreLabel(s.Day, s.Centre)))];
}

export function centreClassOptions(schedule) {
  return schedule
    .slice()
    .sort((a, b) => DAYS.indexOf(a.Day) - DAYS.indexOf(b.Day))
    .map((s) => centreClassLabel(s.Day, s.Centre, s.Class));
}

// Rows for the Excel "Schedule" table: one per Centre/Class/Subject.
export function scheduleRows(schedule) {
  return schedule.flatMap((s) => SUBJECTS.map((sub) => ({ Day: s.Day, CentreClass: centreClassLabel(s.Day, s.Centre, s.Class), Subject: sub })));
}
