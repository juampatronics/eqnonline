"""
Minimal server to show eqn2latex live.
Need to install PLY and Flask in your environment to be ableto run it.

Juan Pablo de la Cruz Gutierrez
"""
import sys
import os
from flask import Flask, send_from_directory, send_file, request, abort
sys.path.append('pyroff')
from pyroff.eqn2latex import Eqn2Latex, EqnException

APP = Flask(__name__)
EQN = Eqn2Latex()


# def escape_chars(s, chars=r'\\'):
#     'escape control characters'
#     s = re.sub(r'([' + ''.join(chars) + '])', r'\\\1', s)
#     return s

@APP.route('/eqn', methods=['GET'])
def eqn():
    '''
    Compile eqn to latex and return the result.
    Queries must be of the form http://localhost:5000/eqn?expr=x%20over%202
    '''
    if 'expr' not in request.args:
        abort(404)
    try:
        latex = EQN.translate(request.args['expr'])
    except (TypeError, EqnException):
        return ""
    return latex


@APP.route("/libs/<path:filename>")
def serve_libs(filename):
    'libraries'
    return send_from_directory('libs', filename)


@APP.route("/src/<path:filename>")
def serve_src(filename):
    'app assests'
    return send_from_directory('src', filename)


@APP.route("/")
def index():
    'main page'
    return send_file('index.html')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', "0.0.0.0")
    APP.run(debug=True, host=host, port=port)
