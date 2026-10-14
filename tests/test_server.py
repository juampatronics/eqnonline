import asyncio
import unittest as ut

from aiohttp.test_utils import TestClient, TestServer
from server import make_app


async def _request(method, path, params=None):
    async with TestClient(TestServer(make_app())) as client:
        resp = await client.request(method, path, params=params)
        body = (await resp.read()).decode('utf-8')
        return resp.status, body


def _run(coro):
    return asyncio.run(coro)


class EqnApiTests(ut.TestCase):
    def test_success(self):
        status, body = _run(_request('POST', '/eqn', {'eqn': 'x over 2'}))
        self.assertEqual(status, 200)
        self.assertEqual(body, r'\frac{x}{2}')

    def test_missing_param(self):
        status, body = _run(_request('POST', '/eqn', {}))
        self.assertEqual(status, 400)
        self.assertIn('eqn', body)

    def test_syntax_error(self):
        status, body = _run(_request('POST', '/eqn', {'eqn': 'left ( x right'}))
        self.assertEqual(status, 422)
        self.assertTrue(body)

    def test_pollution_reset(self):
        async def go():
            async with TestClient(TestServer(make_app())) as client:
                bad = await client.post('/eqn', params={'eqn': 'left ( x right'})
                good = await client.post('/eqn', params={'eqn': 'x over 2'})
                return (bad.status, (await bad.read()).decode('utf-8')), (
                    good.status, (await good.read()).decode('utf-8'))
        (bad_status, _), (good_status, good_body) = _run(go())
        self.assertEqual(bad_status, 422)
        self.assertEqual(good_status, 200)
        self.assertEqual(good_body, r'\frac{x}{2}')

    def test_wrong_method(self):
        status, _ = _run(_request('GET', '/eqn'))
        self.assertEqual(status, 405)

    def test_index(self):
        status, body = _run(_request('GET', '/'))
        self.assertEqual(status, 200)
        self.assertIn('eqnonline', body)

    def test_wheel_static(self):
        async def go():
            async with TestClient(TestServer(make_app())) as client:
                resp = await client.get('/dist/pyroff-0.1.0-py3-none-any.whl')
                body = await resp.read()
                return resp.status, body
        status, body = _run(go())
        self.assertEqual(status, 200)
        self.assertTrue(body.startswith(b'PK'))
