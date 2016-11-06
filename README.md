While developing a documentation tool with two other colleagues, I got to know
a bit about eqn, tbl and troff. These are great tools: easy to learn and produce
high quality results.

We thought, it would be nice if one could use them to generate not only PDFs,
but also high quality HTML files. So this is my attempt to do that. The project
is still in a VERY early stage. So far, there are only two (incomplete) parsers:
one for eqn and another one for tbl.

The basic idea is to generate abstract syntax trees (AST) which are then
translated into to the output format (HTML) or else another intermediate language
which is then used to generated the desired text (eqn -> latex -> text).

Juan Pablo de la Cruz Gutiérrez
Munich, 2016
