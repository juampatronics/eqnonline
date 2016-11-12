#-*- coding: utf-8 -*-
"""
eqn2latex.py converts eqn code into LaTeX and renders it in a HTML page
by making use of KaTeX.

Copyright (C) 2016
Juan Pablo de la Cruz Gutiérrez
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* Neither the name of the Juan Pablo de la Cruz Gutierrez or juampatronics may
  be used to endorse or promote products derived from this software without
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import os
import re
# you may as well add pyroff to PYTHONPATH
sys.path.append('../')
from pyroff.eqn2latex import Eqn2Latex


def escape_chars(s, chars=r'\\'):
    'escape control characters'
    s = re.sub(r'([' + ''.join(chars) + '])', r'\\\1', s)
    return s


header = '''
<!DOCTYPE>
<html>
<head>
    <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.css'>
    <script src='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js'></script>
</head>
<body>
'''

if len(sys.argv) > 1:
    if os.path.isfile(sys.argv[1]):
        with open(sys.argv[1], 'rt') as file:
            input = file.readlines()
    else:
        input = [sys.argv[1]]
else:
    print('''
{} [file] ["eqn expression"]
    converts eqn expressions into LaTeX expressions
'''.format(sys.argv[0]))
    exit(0)

eqn2latex = Eqn2Latex()

template = '''
<div id='{}'></div>
<script>
var element = document.getElementById('{}');
element.innerHTML = katex.renderToString('{}', element);
</script>
'''

footer = '''
</body>
</html>
'''

for id, line in enumerate(input):
    body = template.format('katex' + str(id),
                           'katex' + str(id),
                           escape_chars(eqn2latex.translate(line)))
    print(header + body + footer)
