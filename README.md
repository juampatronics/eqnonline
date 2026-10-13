# How to get started
You only need [uv](https://docs.astral.sh/uv/) — it manages the virtual
environment and all dependencies. The web libraries (katex, codemirror, ...)
are included in the project, so there is nothing else to install.

* Sync the project (creates `.venv`, installs `ply`, `flask`, `pytest` and the
  `pyroff` package)
  * `uv sync`

* Run the test suite
  * `uv run pytest`

* Start the live demo
  * `uv run python eqnonline.py` (starts the server at localhost:5000)
  * try it: `curl 'http://localhost:5000/eqn?expr=x%20over%202'` → `\frac{x}{2}`


# Description
This is a very simple web server so that you can interact live with the eqn to LaTeX
compiler. It is still in a very early stage, so please be forgiving.

The server lives in `eqnonline.py`; the transpilers (eqn→LaTeX, tbl→HTML, pic→SVG)
live in the `pyroff` package, with the test suite in `tests/`.

# Acknowledgments
The nice pi icon enclosed in circle is freely available at [openclipart](https://openclipart.org/detail/220947/Pi%20Symbol%20in%20a%20Circle)
