# How to get started
You need Python (I work with 3.5 but earlier versions of Python 3 should be fine too),
and virtualenv (for simplicity). I decided to also include the libraries in the project,
so that you do not need to install things like bower.

Set up your a virtual environment
  virtualenv venv

Start it
  . venv/bin/activate

Install the necessary libraries
  pip install requirements.txt

And you are good to go
  ./run.sh (starts server at localhost:5000)


# Description
This is a very simple web server so that you can interact live with the eqn to LaTeX
compiler. It is still in a very early stage, so please be forgiving.
