import katex from 'katex';

const input = document.getElementById('eqn-input');
const button = document.getElementById('translate');
const status = document.getElementById('status');
const output = document.getElementById('output');

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
// Translate click retries from scratch.
function beginInit() {
  if (!initPromise) {
    initPromise = initPyodide().then(
      () => {
        status.textContent = '';
        status.classList.remove('info');
        status.hidden = true;
      },
      (err) => {
        initPromise = null;
        throw err;
      },
    );
  }
  return initPromise;
}

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
  try {
    katex.render(latex, output, { throwOnError: false });
  } catch (err) {
    output.textContent = latex;
  }
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

function startRuntime() {
  setHint('Loading Python runtime…');
  button.disabled = true;
  beginInit().then(null, (err) => {
    showError(pythonErrorMessage(err));
  }).finally(() => {
    button.disabled = false;
  });
}

async function translate() {
  const code = input.value.trim();
  if (!code) {
    showError('Type an eqn expression first.');
    return;
  }
  button.disabled = true;
  try {
    if (!pyTranslate) {
      setHint('Loading Python runtime…');
      await beginInit();
    }
    showLatex(pyTranslate(code));
  } catch (err) {
    showError(pythonErrorMessage(err));
  } finally {
    button.disabled = false;
  }
}

button.addEventListener('click', translate);
input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    translate();
  }
});

startRuntime();
