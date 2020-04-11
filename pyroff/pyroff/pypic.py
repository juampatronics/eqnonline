# -*- coding: utf-8 -*-
"""
pyeqn a parser for the eqn language described in
  A system for Typesetting Mathematics
  Brian W. Kernighan and Lorinda L. Cherry
  CACM, March, 1975

Copyright (C) 2020
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

from ply import lex
from ply import yacc
import re
import inspect


class PicException(Exception):
    'Trigger errors ought to wrong eqn syntax'
    pass


primitives = ['CIRCLE', 'ELLIPSE', 'LINE', 'ARC', 'ARROW', 'BOX', 'SPLINE']
commands = ['ABOVE', 'BELOW', 'MOVE',
            'UP', 'DOWN', 'RIGHT', 'LEFT', 'THEN', 'SAME', 'END', 'TOP', 'BOTTOM']
references = ['LAST', 'OF', 'FROM', 'TO']
attributes = ['DASHED', 'DOTTED']
default_radius = 0.25  # inches


def t_WIDTH(t):
    r'(width|wid)'
    # better return canonical form: 'width'
    return t


def t_HEIGHT(t):
    r'(height|ht)'
    # better return canonical form
    return t


def t_RADIUS(t):
    r'(radius|rad)'
    return t


def t_DIAMETER(t):
    r'(diameter|diam)'
    return t


def t_NUMBER(t):
    r'-?[0-9]*\.[0-9]+'
    return float(t)


def t_LABEL(t):
    r'"[^"]+"'
    return t


def t_CMDEND(t):
    r';'
    return t


def t_FIRST(t):
    r'(first|1st)'
    return t


def t_SECOND(t):
    r'(second|2nd)'
    return t


tokenizer = lex.lex()

if __name__ == "__main__":
    import unittest as ut

    ut.main()
