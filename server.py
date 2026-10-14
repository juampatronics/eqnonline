import os

from aiohttp import web
from pyroff import pyeqn
from pyroff.eqn2latex import Eqn2Latex

EQN = Eqn2Latex()


def translate(code):
    'reset PLY exclusive-state stack, then transpile'
    pyeqn.tokenizer.begin('INITIAL')
    return EQN.translate(code)


async def eqn(request: web.Request) -> web.Response:
    code = request.rel_url.query.get('eqn')
    if code is None:
        raise web.HTTPBadRequest(
            text='Missing eqn code: use /eqn?eqn=<code>',
            content_type='text/plain')
    try:
        latex = translate(code)
    except Exception as exc:
        message = str(exc) or 'Invalid eqn syntax'
        raise web.HTTPUnprocessableEntity(
            text=message, content_type='text/plain') from exc
    response = web.Response(text=latex, content_type='text/plain')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


async def index(request: web.Request) -> web.StreamResponse:
    return web.FileResponse(os.path.join(os.path.dirname(__file__), 'index.html'))


async def favicon(request: web.Request) -> web.StreamResponse:
    root = os.path.dirname(os.path.abspath(__file__))
    return web.FileResponse(os.path.join(root, 'favicon.ico'))


def make_app() -> web.Application:
    app = web.Application()
    app.router.add_post('/eqn', eqn)
    app.router.add_get('/', index)
    app.router.add_get('/favicon.ico', favicon)
    app.router.add_static('/dist', os.path.join(os.path.dirname(__file__), 'dist'))
    app.router.add_static('/src', os.path.join(os.path.dirname(__file__), 'src'))
    return app


if __name__ == '__main__':
    web.run_app(make_app(),
                host=os.environ.get('HOST', '0.0.0.0'),
                port=int(os.environ.get('PORT', '8080')))
