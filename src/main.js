import katex from 'katex';
import {
  debounceTime,
  distinctUntilChanged,
  filter,
  from,
  fromEvent,
  map,
  merge,
  switchMap,
  timeout,
  catchError,
  EMPTY,
} from 'rxjs';

const input = document.getElementById('eqn-input');
const status = document.getElementById('status');
const output = document.getElementById('output');
const autoDelay = document.getElementById('auto-delay');
const autoLabel = document.getElementById('auto-label');

// ------------------------------------------------------------------ brand
const BRAND = '\\textcolor{#3355aa}{\\varepsilon qn}\\text{online}';

function renderMath(el, latex) {
  try {
    katex.render(latex, el, { throwOnError: false });
  } catch (err) {
    el.textContent = latex;
  }
}

renderMath(document.getElementById('brand'), BRAND);

// --------------------------------------------------------- reference panel
// Examples and the exact LaTeX the transpiler produces (each verified
// against pyroff.eqn2latex). Clicking a row loads the eqn code into the
// editor and compiles it immediately.
const EXAMPLES = [
  ['x over 2', '\\frac{x}{2}'],
  ['x sub i', 'x_{i}'],
  ['x sub i sup n', 'x_{i}^{n}'],
  ['sqrt a sub 2 + b sub 2', '\\sqrt{a_{2}} + b_{2}'],
  ['sum from n=1 to N x sub n', '\\sum_{n=1}^{N} x_{n}'],
  ['prod from i=1 to n a sub i', '\\prod_{i=1}^{n} a_{i}'],
  ['int from 0 to 1 e sup x dx', '\\int_{0}^{1} e^{x} dx'],
  ['PSI ( alpha + beta )', '\\Psi(\\alpha + \\beta)'],
  ['pi over 2', '\\frac{\\pi}{2}'],
  ['left ( a + b right)', '\\left( a + b \\right)'],
  ['a partial b', 'a \\partial b'],
];

(function buildReference() {
  const tbody = document.querySelector('#ref-table tbody');
  for (const [code, latex] of EXAMPLES) {
    const tr = document.createElement('tr');
    tr.tabIndex = 0;
    const tdCode = document.createElement('td');
    tdCode.className = 'code';
    tdCode.textContent = code;
    const tdMath = document.createElement('td');
    renderMath(tdMath, latex);
    tr.append(tdCode, tdMath);
    tbody.append(tr);
  }
})();

// --------------------------------------------------------------- UI state
function setHint(message) {
  status.classList.add('info');
  status.textContent = message;
  status.hidden = false;
}

function showError(message) {
  output.innerHTML = '';
  status.classList.remove('info');
  status.textContent = message;
  status.hidden = false;
}

function showLatex(latex) {
  status.hidden = true;
  output.innerHTML = '';
  renderMath(output, latex);
}

// Pyodide surfaces Python exceptions as JS Errors whose message is the
// full traceback; report only the final exception line.
function pythonErrorMessage(err) {
  const msg = (err && err.message) || '';
  const lines = msg.split('\n').map((line) => line.trim()).filter(Boolean);
  const last = lines.length ? lines[lines.length - 1] : '';
  // empty-message AssertionError is the parser's "invalid syntax" signal
  if (!last || last === 'AssertionError') {
    return 'Invalid eqn syntax';
  }
  return last;
}

// ------------------------------------------------------- Python runtime
const PYODIDE_INDEX = 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/';
const PLY_WHEEL =
  'https://files.pythonhosted.org/packages/a3/58/35da89ee790598a0700ea49b2a66594140f44dec458c07e8e3d4979137fc/ply-3.11-py2.py3-none-any.whl';

const SETUP = `
import pyroff.pyeqn as _pyeqn
from pyroff.eqn2latex import Eqn2Latex
_EQN = Eqn2Latex()

def translate(code):
    _pyeqn.tokenizer.begin('INITIAL')
    return _EQN.translate(code)
`;

let pyTranslate = null;
let initPromise = null;

async function initPyodide() {
  const pyodide = await globalThis.loadPyodide({ indexURL: PYODIDE_INDEX });
  await pyodide.loadPackage([PLY_WHEEL, 'dist/pyroff-0.1.0-py3-none-any.whl']);
  await pyodide.runPythonAsync(SETUP);
  pyTranslate = pyodide.globals.get('translate');
}

// One shared initialization; a failure clears initPromise so a later
// request retries from scratch.
function beginInit() {
  if (!initPromise) {
    initPromise = initPyodide().then(null, (err) => {
      initPromise = null;
      throw err;
    });
  }
  return initPromise;
}

function translate(code) {
  return beginInit().then(() => pyTranslate(code));
}

// ------------------------------------------------------ reactive pipeline
// The slider is the single source of truth for the debounce delay:
// delayMs() reads the current slider value at fire time, so moving the
// slider immediately changes the pending debounce.
function delayMs() {
  const delay = Number(autoDelay.value);
  return Number.isInteger(delay) && delay > 0 ? delay : 0;
}

function updateAutoLabel() {
  autoLabel.textContent = delayMs() ? delayMs() + ' ms' : 'off';
}

const TRANSLATE_TIMEOUT_MS = 15000;

// Ctrl/Cmd-Enter bypasses the debounce for immediate translation.
const manual$ = fromEvent(input, 'keydown').pipe(
  filter((event) => event.key === 'Enter' && (event.ctrlKey || event.metaKey)),
  map((event) => {
    event.preventDefault();
    return input.value.trim();
  }),
);

// Example clicks: load the code into the editor, focus it, and compile.
const examples$ = fromEvent(document.getElementById('ref-table'), 'click').pipe(
  filter((event) => {
    const tr = event.target && event.target.closest('tr');
    return tr && tr.querySelector('.code');
  }),
  map((event) => event.target.closest('tr').querySelector('.code').textContent),
);

// Debounced auto-compile: debounce delay is read from the slider at
// fire time, so moving the slider immediately re-arms the pending
// debounce with the new delay.
const debouncedInput$ = fromEvent(input, 'input').pipe(
  map(() => input.value.trim()),
  debounceTime(() => delayMs()),
  distinctUntilChanged(),
  filter((code) => code.length > 0),
);

// A single pipeline for all three sources. switchMap cancels the
// previous in-flight translation when a new one arrives, so the UI
// always reflects the latest code. Errors are caught and reported; the
// stream stays alive so the next input can translate normally.
merge(debouncedInput$, manual$, examples$)
  .pipe(
    switchMap((code) =>
      from(translate(code)).pipe(
        timeout(TRANSLATE_TIMEOUT_MS),
        catchError((err) => {
          showError(pythonErrorMessage(err));
          return EMPTY;
        }),
      ),
    ),
  )
  .subscribe((latex) => showLatex(String(latex)));

// Example clicks also load the code into the editor.
examples$.subscribe((code) => {
  input.value = code;
  input.focus();
});

// ------------------------------------------------------------- event wiring
autoDelay.addEventListener('input', () => {
  try {
    localStorage.setItem('eqn-autodelay', autoDelay.value);
  } catch {}
  updateAutoLabel();
});

const storedRaw = localStorage.getItem('eqn-autodelay');
if (storedRaw !== null) {
  const storedDelay = Number(storedRaw);
  if (Number.isInteger(storedDelay) && storedDelay >= 0 && storedDelay <= 2000) {
    autoDelay.value = storedDelay;
  }
}
updateAutoLabel();

setHint('Loading Python runtime…');
beginInit().then(
  () => {
    status.textContent = '';
    status.hidden = true;
  },
  (err) => {
    showError(pythonErrorMessage(err));
  },
);
