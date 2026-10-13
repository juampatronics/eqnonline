import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from pyroff.eqn2latex import Eqn2Latex

    return Eqn2Latex, mo


@app.cell
def _(Eqn2Latex):
    eqn = Eqn2Latex()
    return (eqn,)


@app.cell(hide_code=True)
def _(mo):
    code = mo.ui.text_area().form()
    code
    return (code,)


@app.cell(hide_code=True)
def _(code, eqn, mo):
    mo.md(f'''
    \[
    {eqn.translate(code.value)}
    \]
    ''')
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
