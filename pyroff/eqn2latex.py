# -*- coding: utf-8 -*-
"""
eqn2latex.py converts eqn code into LaTeX

Copyright (C) 2016-2017
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

from .pyeqn import EqnException, treebuilder
import sys
import re


symbols_map = {
    '>=': '\\geq',
    '<=': '\\leq',
    '<<': '\\ll',
    '>>': '\\gg',
    'inter': '\\cap',
    'union': '\\cup',
    '->': '\\to',
    'grad': '\\nabla',
    '!=': '\\ne',
    '==': '\\equiv',
    'inf': '\\infty',
    '+-': '\\pm',
}


def space(s):
    if s == '^':
        return r'\;'
    if s == '~':
        return r'\quad'
        # return r'\ '
    return s


def escape_chars(s, chars=r'\\'):
    'escape control characters'
    s = re.sub(r'([' + ''.join(chars) + '])', r'\\\1', s)
    return s


def eqn_text(*args):
    return ' '.join([space(a) for a in args])


def eqn_bracketed(*args):
    return ' '.join(args)


def eqn_sup(*args):
    return args[0] + '^{' + args[1] + '}'


def eqn_sub(*args):
    return args[0] + '_{' + args[1] + '}'


def eqn_over(*args):
    return r'\frac{' + args[0] + '}{' + args[1] + '}'


def eqn_special_char(char):
    if char == char.upper():
        return '\\' + char[0] + char[1:].lower()
    if char in symbols_map:
        return symbols_map[char]
    return '\\' + char


def eqn_from(*args):
    return args[0] + '_{' + args[1] + '}'


def eqn_to(*args):
    return args[0] + '^{' + args[1] + '}'


def eqn_sum(*args):
    return '\\sum'


def eqn_sqrt(*args):
    return '\\sqrt{' + ' '.join(args) + '}'


def eqn_left(*args):
    return '\\left' + args[0]


def eqn_right(*args):
    return '\\right' + args[0]


def eqn_mathop(*args):
    return symbols_map.get(args[0], '\\' + ''.join(*args))


def eqn_brackets(*args):
    return ' '.join(args)


class Eqn2Latex:
    def __init__(self):
        self._translator = treebuilder.custom(sys.modules[__name__], 'eqn_')

    def translate(self, s):
        return self._translator.translate(s)

    def translate_file(self, filename):
        return self._translator.translate_file(filename)


