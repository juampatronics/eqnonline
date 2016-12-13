# -*- coding: utf-8 -*-
"""
eqn.py the equivalent of the eqn preprocessor

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
import re
# you may as well add pyroff to PYTHONPATH
sys.path.append('../')
from pyroff.eqn2latex import Eqn2Latex

input = open(sys.argv[1], 'r') if len(sys.argv) > 1 else sys.stdin
eqnlatex = Eqn2Latex()

for line in input:
    if not re.match('^\.EQ', line):
        print(line, end='')
    else:
        print(line, end='')
        lines = []
        line = input.readline()[:-1]
        while not re.match('^\.EN', line):
            lines.extend(line)
            line = input.readline()[:-1]
        print(eqnlatex.translate(''.join(lines)))
        print(line, end='')
