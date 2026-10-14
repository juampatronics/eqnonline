'use strict';

const input = document.getElementById('eqn-input');
const button = document.getElementById('translate');
const status = document.getElementById('status');
const output = document.getElementById('output');

function showError(message) {
  output.textContent = '';
  status.textContent = message;
  status.hidden = false;
}

function showLatex(latex) {
  status.hidden = true;
  output.textContent = latex;
}

async function translate() {
  const code = input.value.trim();
  if (!code) {
    showError('Type an eqn expression first.');
    return;
  }
  button.disabled = true;
  try {
    const resp = await fetch('/eqn?eqn=' + encodeURIComponent(code), {
      method: 'POST'
    });
    const text = await resp.text();
    if (resp.ok) {
      showLatex(text);
    } else {
      showError('HTTP ' + resp.status + ': ' + text);
    }
  } catch (err) {
    showError('Could not reach the eqn server: ' + err);
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
