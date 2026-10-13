# -*- coding: utf-8 -*-
"""
PIC - A Language for Typesetting Graphics
  Brian W. Kernighan
  Software Practice Experience (12): 1–20, 1982

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
from .utils import Translator
import sys


class PicException(Exception):
    'Trigger errors ought to wrong eqn syntax'
    pass


t_ANY_ignore = ' \t'

primitives = ['CIRCLE', 'ELLIPSE', 'LINE', 'ARC', 'ARROW', 'BOX', 'SPLINE']
commands = ['ABOVE', 'BELOW', 'MOVE',
            'UP', 'DOWN', 'RIGHT', 'LEFT', 'THEN', 'SAME', 'END', 'TOP', 'BOTTOM']
references = ['LAST', 'OF', 'FROM', 'TO', 'LOWER', 'UPPER']
attributes = ['DASHED', 'DOTTED']
default_radius = 0.25  # inches


def gen_reserved_dict(words_list, lowercase=False):
    return dict((k.lower() if lowercase else k, k) for k in words_list)


reserved = gen_reserved_dict(commands, True)
reserved.update(gen_reserved_dict(primitives, True))
reserved.update(gen_reserved_dict(references, True))
reserved.update(gen_reserved_dict(attributes, True))

tokens = ['WIDTH', 'HEIGHT', 'RADIUS', 'DIAMETER', 'NUMBER', 'LABEL', 'CMDEND',
          'FIRST', 'SECOND'] + list(reserved.values())


def t_WIDTH(t):
    r'(width|wid)'
    t.value = 'width'
    return t


def t_HEIGHT(t):
    r'(height|ht)'
    t.value = 'height'
    return t


def t_RADIUS(t):
    r'(radius|rad)'
    t.value = 'radius'
    return t


def t_DIAMETER(t):
    r'(diameter|diam)'
    t.value = 'diameter'
    return t


def t_LABEL(t):
    r'"[^"]+"'
    t.value = t.value[1:-1]
    return t


def t_CMDEND(t):
    r'(;|\n)'
    return t


def t_FIRST(t):
    r'(first|1st)'
    t.value = 'first'
    return t


def t_SECOND(t):
    r'(second|2nd)'
    t.value = 'second'
    return t


def t_NUMBER(t):
    r'[0-9]*\.?[0-9]+'
    t.value = float(t.value)
    return t


def t_RESERVED(t):
    r'[a-z0-9]+'
    t.type = reserved.get(t.value)
    if not t.type:
        raise lex.LexError('Unexpected token {}'.format(t.value), str(t))
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_ANY_error(t):
    print("Illegal character '%s' at line %d" % (t.value[0],
                                                 t.lexer.lineno))


tokenizer = lex.lex()

# parser ============================================================


def picnode(ntype, *args):
    return (ntype, args)


def p_error(p):
    print("Error while parsing : ", p)


def p_pic(p):
    '''pic : element
           | element pic'''
    print('p_pic: ', *p)
    p[0] = p[1] + p[2] if len(p) > 2 else p[1]


def p_element(p):
    '''element : nextcmd
               | direction
               | primitive
               | move'''
    print('p_element: ', *p)
    p[0] = p[1]


def p_nextcmd(p):
    'nextcmd : CMDEND element'
    print('p_nextcmd: ', *p)
    p[0] = p[2]


def p_direction(p):
    '''direction : DOWN
                 | UP
                 | RIGHT
                 | LEFT'''
    print('p_direction: ', *p)
    p[0] = picnode('direction', p[1])


def p_primitive(p):
    '''primitive : circle
                 | line
                 | box'''
    print('p_primitive: ', *p)
    p[0] = picnode('primitive', *p[1])


def p_circle(p):
    '''circle : CIRCLE cattrs
              | CIRCLE'''
    print('p_circle: ', *p)
    p[0] = picnode('circle', *p[2]) if len(p) > 2 else picnode('circle', None)


def p_cattrs(p):
    '''cattrs : cattr cattrs
              | cattr'''
    print('p_cattrs: ', *p)
    p[0] = p[1] + p[2] if len(p) > 2 else p[1]


def p_cattr(p):
    '''cattr : RADIUS NUMBER
             | label'''
    print('p_cattr: ', *p)
    p[0] = picnode('radius', p[2]) if len(p) > 2 else p[1]


def p_label(p):
    '''label : LABEL label
             | LABEL'''
    print('p_label: ', *p)
    p[0] = picnode('label', p[1]) + \
        p[2] if len(p) > 2 else picnode('label', p[1])


def p_line(p):
    '''line : LINE lattrs
            | LINE'''
    print('p_line: ', *p)
    p[0] = picnode('line', *p[2]) if len(p) > 2 else picnode('line', None)


def p_lattrs(p):
    '''lattrs : lattr lattrs
              | lattr'''
    print('p_lattrs: ', *p)
    p[0] = p[1] + p[2] if len(p) > 2 else p[1]


def p_lattr(p):
    '''lattr : lstyle
             | LABEL tposition'''
    print('p_lattr: ', *p)
    p[0] = picnode('label', p[1]) + p[2] if len(p) > 2 else p[1]


def p_tposition(p):
    '''tposition : ABOVE
                 | BELOW'''
    print('p_tposition: ', *p)
    p[0] = picnode('tposition', p[1])


def p_lstyle(p):
    '''lstyle : DOTTED
              | DASHED'''
    print('p_lstyle: ', *p)
    p[0] = picnode('lstyle', p[1])


def p_box(p):
    '''box : BOX battrs
           | BOX'''
    print('p_box: ', *p)
    p[0] = picnode('box', *p[2]) if len(p) > 2 else picnode('box', None)


def p_battrs(p):
    '''battrs : battr battrs
              | battr'''
    print('p_cattrs: ', *p)
    p[0] = p[1] + p[2] if len(p) > 2 else p[1]


def p_battr(p):
    '''battr : WIDTH NUMBER
             | HEIGHT NUMBER
             | lstyle
             | label'''
    print('p_battr: ', *p)
    p[0] = picnode(p[1], p[2]) if len(p) > 2 else p[1]


def p_single_move(p):
    'move : MOVE'
    p[0] = picnode('move', None)


def p_move_dist(p):
    '''move : MOVE direction
            | MOVE direction NUMBER'''
    raise NotImplementedError('p_move_dist')


treebuilder = Translator(yacc.yacc(start='pic'),
                         ['circle', 'box', 'radius',
                          'width', 'height', 'label', 'primitive'])

