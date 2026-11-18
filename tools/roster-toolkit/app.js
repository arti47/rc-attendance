import { parseCSV, validate, formGroups, centreClassOptions, scheduleRows } from './lib.js';

const $ = (id) => document.getElementById(id);
const readFile = (input) => new Promise((res, rej) => {
  const f = input.files[0];
  if (!f) return res(null);
  const r = new FileReader();
  r.onload = () => res(r.result);
  r.onerror = rej;
  r.readAsText(f);
});
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

let defaultSchedule = null;
async function loadDefaultSchedule() {
  if (defaultSchedule) return defaultSchedule;
  const res = await fetch('schedule.csv'); // same-origin static file, no student data
  defaultSchedule = parseCSV(await res.text());
  return defaultSchedule;
}

$('run').addEventListener('click', async () => {
  const rText = await readFile($('roster'));
  if (!rText) { alert('Choose the roster CSV first.'); return; }
  const sText = await readFile($('schedule'));
  const roster = parseCSV(rText);
  const schedule = sText ? parseCSV(sText) : await loadDefaultSchedule();
  const { errors, warnings } = validate(roster, schedule);

  $('results').hidden = false;
  $('summary').innerHTML = errors.length
    ? `<p class="err"><b>${errors.length} error(s)</b> – fix in the workbook before updating FormSG.</p>`
    : `<p class="ok"><b>OK</b> – ${roster.length} students, ${schedule.length} centre-classes.</p>`;
  $('issues').innerHTML = [...errors.map((e) => `<li class="err">${esc(e)}</li>`), ...warnings.map((w) => `<li class="warn">${esc(w)}</li>`)].join('');

  $('outputs').hidden = errors.length > 0;
  if (errors.length) return;
  $('ccOpts').value = centreClassOptions(schedule).join('\n');
  $('schedRows').value = scheduleRows(schedule).map((r) => [r.Day, r.CentreClass, r.Subject].join('\t')).join('\n');
  $('groups').innerHTML = formGroups(roster).map((g, i) => `
    <details><summary>${esc(g.label)} (${g.options.length - 1} students)</summary>
      <textarea id="g${i}" readonly>${esc(g.options.join('\n'))}</textarea>
      <button data-copy="g${i}">Copy options</button>
    </details>`).join('');
});

document.addEventListener('click', async (e) => {
  const id = e.target?.dataset?.copy;
  if (!id) return;
  await navigator.clipboard.writeText($(id).value);
  e.target.textContent = 'Copied';
  setTimeout(() => { e.target.textContent = e.target.textContent === 'Copied' ? 'Copy' : e.target.textContent; }, 1200);
});
