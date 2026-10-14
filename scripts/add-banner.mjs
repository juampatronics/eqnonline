// Stamp the copyright header (with build date) at the top of the bundle.
// Terser 8 dropped its `banner` option, so this runs post-build.
// Re-stamps on every run: any previous leading block comment is replaced.
import fs from 'node:fs';

const file = 'src/main.bundle.js';
const date = new Date().toISOString().slice(0, 10);
const banner = `/*!
 * eqnonline — eqn → LaTeX web app (client bundle)
 * Copyright (c) ${new Date().getFullYear()} Juan Pablo de la Cruz Gutiérrez
 * Licensed under the BSD 3-Clause "New" or "Revised" License
 * Compiled: ${date}
 */
`;
let code = fs.readFileSync(file, 'utf8');
if (code.startsWith('/*!')) {
  const end = code.indexOf('*/');
  if (end !== -1 && end < 400) {
    code = code.slice(end + 2).replace(/^\n/, '');
  }
}
if (code.startsWith(banner)) {
  console.log(`banner up to date in ${file}`);
  process.exit(0);
}
fs.writeFileSync(file, banner + code);
console.log(`banner stamped in ${file} (compiled ${date})`);
