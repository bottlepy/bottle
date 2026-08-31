import asyncio
import unittest
import bottle
from bottle import Bottle, HTTPError, HTTPResponse, response, request, ASGIAdapter


class TestASGIAdapter(unittest.TestCase):
    def setUp(self):
        self.app = Bottle()
        self.asgi = self.app.to_asgi()

    def _run(self, coro):
        return asyncio.run(coro)

    async def _send_asgi_request(self, method='GET', path='/', query_string=b'', headers=None, body=b''):
        messages_sent = []

        raw_headers = []
        if headers:
            for k, v in headers.items():
                raw_headers.append((k.encode('latin1'), v.encode('latin1')))

        scope = {
            'type': 'http',
            'asgi': {'version': '3.0', 'spec_version': '2.0'},
            'http_version': '1.1',
            'method': method,
            'scheme': 'http',
            'path': path,
            'raw_path': path.encode('latin1'),
            'query_string': query_string,
            'root_path': '',
            'headers': raw_headers,
            'client': ('127.0.0.1', 54321),
            'server': ('localhost', 8080),
        }

        async def receive():
            return {
                'type': 'http.request',
                'body': body,
                'more_body': False,
            }

        async def send(msg):
            messages_sent.append(msg)

        await self.asgi(scope, receive, send)
        return messages_sent

    def test_asgi_property_and_wrapper(self):
        self.assertIsInstance(self.app.asgi, ASGIAdapter)
        self.assertIsInstance(self.app.to_asgi(), ASGIAdapter)

    def test_basic_get_request(self):
        @self.app.route('/hello')
        def hello():
            return "Hello ASGI World!"

        messages = self._run(self._send_asgi_request('GET', '/hello'))
        start_msg = messages[0]
        body_msg = messages[1]

        self.assertEqual(start_msg['type'], 'http.response.start')
        self.assertEqual(start_msg['status'], 200)
        self.assertEqual(body_msg['type'], 'http.response.body')
        self.assertEqual(body_msg['body'], b'Hello ASGI World!')

    def test_async_route_handler(self):
        @self.app.route('/async_hello')
        async def async_hello():
            await asyncio.sleep(0.01)
            return "Hello from Async Handler!"

        messages = self._run(self._send_asgi_request('GET', '/async_hello'))
        self.assertEqual(messages[0]['status'], 200)
        self.assertEqual(messages[1]['body'], b'Hello from Async Handler!')

    def test_query_params_and_path_args(self):
        @self.app.route('/greet/<name>')
        def greet(name):
            greeting = request.query.get('greeting', 'Hello')
            return f"{greeting}, {name}!"

        messages = self._run(self._send_asgi_request('GET', '/greet/Alice', query_string=b'greeting=Welcome'))
        self.assertEqual(messages[0]['status'], 200)
        self.assertEqual(messages[1]['body'], b'Welcome, Alice!')

    def test_post_body_json(self):
        @self.app.route('/echo', method='POST')
        def echo():
            return request.body.read()

        data = b'{"key": "value"}'
        headers = {'Content-Type': 'application/json', 'Content-Length': str(len(data))}
        messages = self._run(self._send_asgi_request('POST', '/echo', headers=headers, body=data))
        self.assertEqual(messages[0]['status'], 200)
        self.assertEqual(messages[1]['body'], data)

    def test_custom_headers_and_status(self):
        @self.app.route('/custom')
        def custom():
            response.status = 201
            response.set_header('X-Custom-Header', 'BottleASGI')
            return "Created"

        messages = self._run(self._send_asgi_request('GET', '/custom'))
        self.assertEqual(messages[0]['status'], 201)
        headers_dict = {k.decode('latin1'): v.decode('latin1') for k, v in messages[0]['headers']}
        self.assertEqual(headers_dict.get('x-custom-header'), 'BottleASGI')

    def test_404_not_found(self):
        messages = self._run(self._send_asgi_request('GET', '/nonexistent_route_404'))
        self.assertEqual(messages[0]['status'], 404)

    def test_500_exception_handling(self):
        @self.app.route('/crash')
        def crash():
            raise ValueError("Intentional crash for test")

        messages = self._run(self._send_asgi_request('GET', '/crash'))
        self.assertEqual(messages[0]['status'], 500)

    def test_lifespan_protocol(self):
        started = []
        stopped = []

        @self.app.hook('asgi_startup')
        def on_start():
            started.append(True)

        @self.app.hook('asgi_shutdown')
        def on_stop():
            stopped.append(True)

        async def test_lifespan():
            scope = {'type': 'lifespan', 'asgi': {'version': '3.0'}}
            queue = [
                {'type': 'lifespan.startup'},
                {'type': 'lifespan.shutdown'},
            ]
            sent_messages = []

            async def receive():
                return queue.pop(0)

            async def send(msg):
                sent_messages.append(msg)

            await self.asgi(scope, receive, send)
            return sent_messages

        msgs = self._run(test_lifespan())
        self.assertEqual(msgs[0]['type'], 'lifespan.startup.complete')
        self.assertEqual(msgs[1]['type'], 'lifespan.shutdown.complete')
        self.assertTrue(started)
        self.assertTrue(stopped)


if __name__ == '__main__':
    unittest.main()
