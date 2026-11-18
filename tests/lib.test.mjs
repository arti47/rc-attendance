import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parseCSV, studentKey, validate, formGroups, centreClassOptions, scheduleRows, NONE_OPTION, lateGroups, centreOptions } from '../tools/roster-toolkit/lib.js';

const read = (p) => parseCSV(readFileSync(new URL(p, import.meta.url), 'utf8'));
const schedule = read('../data/schedule.csv');
const roster = read('../templates/roster_template.csv');

test('key format matches Excel formula', () => {
  assert.equal(studentKey({ StudentName: ' Alex  Tan ', SchoolCode: 'dps', Subject: 'm', Class: '1' }), 'Alex Tan (DPS) M1');
});

test('csv parser handles quotes, CRLF, BOM', () => {
  const r = parseCSV('﻿A,B\r\n"x, y","he said ""hi"""\r\n');
  assert.deepEqual(r, [{ A: 'x, y', B: 'he said "hi"' }]);
});

test('template roster validates clean against schedule', () => {
  const { errors } = validate(roster, schedule);
  assert.deepEqual(errors, []);
});

test('detects duplicates, bad subject, comma in name, unscheduled centre', () => {
  const bad = [
    { ...roster[0] },
    { ...roster[0] },
    { ...roster[1], Subject: 'X' },
    { ...roster[1], StudentName: 'Tan, Ah Kow' },
    { ...roster[1], Centre: 'Nowhere School' },
  ];
  const { errors } = validate(bad, schedule);
  assert.ok(errors.some((e) => e.includes('duplicate')));
  assert.ok(errors.some((e) => e.includes('Subject')));
  assert.ok(errors.some((e) => e.includes(', * ?')));
  assert.ok(errors.some((e) => e.includes('not in schedule')));
});

test('substring key collision warned', () => {
  const r = [{ ...roster[0], StudentName: 'Tan Wei' }, { ...roster[0], StudentName: 'Ah Tan Wei' }];
  assert.ok(validate(r, schedule).warnings.some((w) => w.includes('contained')));
});

test('form groups start with NONE option', () => {
  const g = formGroups(roster);
  assert.equal(g.length, 4);
  for (const x of g) assert.equal(x.options[0], NONE_OPTION);
});

test('schedule expands to 3 subjects per centre-class', () => {
  assert.equal(scheduleRows(schedule).length, schedule.length * 3);
  assert.equal(centreClassOptions(schedule)[0], 'Mon | Yew Tee Primary School | C1');
});

test('late groups: one per centre-day, NONE first, sorted', () => {
  const g = lateGroups(roster);
  assert.deepEqual(g.map((x) => x.label), ['Mon | Geylang Methodist School', 'Mon | Yew Tee Primary School', 'Tue | Innova Primary School']);
  assert.equal(g[1].options.length, 3);
  assert.equal(g[1].options[0], NONE_OPTION);
  assert.equal(centreOptions(schedule).length, 15);
});
