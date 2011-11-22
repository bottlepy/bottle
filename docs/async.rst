Primer to Asynchronous Applications
===================================

Asynchronous design patterns don't mix well with the synchronous nature of `WSGI <http://www.python.org/dev/peps/pep-3333/>`_. This is why most asynchronous frameworks (tornado, twisted, ...) implement a specialized API to expose their asynchronous features. Bottle is a WSGI framework and shares the synchronous nature of WSGI, but thanks to the awesome `gevent project <http://www.gevent.org/>`_, it is still possible to write asynchronous applications with bottle. This article documents the usage of Bottle with Asynchronous WSGI.

The Limits of Synchronous WSGI
-------------------------------

Briefly worded, the `WSGI specification (pep 3333) <http://www.python.org/dev/peps/pep-3333/>`_ defines a request/response circle as follows: The application callable is invoked once for each request and must return a body iterator. The server then iterates over the body and writes each chunk to the socket. As soon as the body iterator is exhausted, the client connection is closed.

Simple enough, but there is a snag: All this happens synchronously. If your application needs to wait for data (IO, sockets, databases, ...), it must either yield empty strings (busy wait) or block the current thread. Both solutions occupy the handling thread and prevent it from answering new requests. There is consequently only one ongoing request per thread.

Most servers limit the number of threads to avoid their relatively high overhead. Pools of 20 or less threads are common. As soon as all threads are occupied, any new connection is stalled. The server is effectively dead for everyone else. If you want to implement a chat that uses long-polling ajax requests to get real-time updates, you'd reach the limited at 20 concurrent connections. That's a pretty small chat.

Greenlets to the rescue
------------------------

Most servers limit the size of their worker pools to a relatively low number of concurrent threads, due to the high overhead involved in switching between and creating new threads. While threads are cheap compared to processes (forks), they are still expensive to create for each new connection.

The `gevent <http://www.gevent.org/>`_ module adds *greenlets* to the mix. Greenlets behave similar to traditional threads, but are very cheap to create. A gevent-based server can spawn thousands of greenlets (one for each connection) with almost no overhead. Blocking individual greenlets has no impact on the servers ability to accept new requests. The number of concurrent connections is virtually unlimited.

This makes creating asynchronous applications incredibly easy, because they look and feel like synchronous applications. A gevent-based server is actually not asynchronous, but massively multi-threaded. Here is an example::

    from gevent import monkey; monkey.patch_all()

    from time import sleep
    from bottle import route, run

    @route('/stream')
    def stream():
        yield 'START'
        sleep(3)
        yield 'MIDDLE'
        sleep(5)
        yield 'END'

    run(host='0.0.0.0', port=8080, server='gevent')

The first line is important. It causes gevent to monkey-patch most of Python's blocking APIs to not block the current thread, but pass the CPU to the next greenlet instead. It actually replaces Python's threading with gevent-based pseudo-threads. This is why you can still use ``time.sleep()`` which would normally block the whole thread. If you don't feel comfortable with monkey-patching python build-ins, you can use the corresponding gevent functions (``gevent.sleep()`` in this case).

If you run this script and point your browser to ``http://localhost:8080/stream``, you should see `START`, `MIDDLE`, and `END` show up one by one (rather than waiting 8 seconds to see them all at once). It works exactly as with normal threads, but now your server can handle thousands of concurrent requests without any problems.

.. note::

    Some browsers buffer a certain amount of data before they start rendering a
    page. You might need to yield more than a few bytes to see an effect in
    these browsers. Additionally, many browsers have a limit of one concurrent
    connection per URL. If this is the case, you can use a second browser or a
    benchmark tool (e.g. `ab` or `httperf`) to measure performance.

Event Callbacks
---------------

A very common design pattern in asynchronous frameworks (including tornado, twisted, node.js and friends) is to use non-blocking APIs and bind callbacks to asynchronous events. The socket object is kept open until it is closed explicitly to allow callbacks to write to the socket at a later point. Here is an example based on the `tornado library <http://www.tornadoweb.org/documentation#non-blocking-asynchronous-requests>`_::

    class MainHandler(tornado.web.RequestHandler):
        @tornado.web.asynchronous
        def get(self):
            worker = SomeAsyncWorker()
            worker.on_data(lambda chunk: self.write(chunk))
            worker.on_finish(lambda: self.finish())

The main benefit is that the request handler terminates early. The handling thread can move on and accept new requests while the callbacks continue to write to sockets of previous requests. This is how these frameworks manage to process a lot of concurrent requests with only a small number of OS threads.

With Gevent+WSGI, things are different: First, terminating early has no benefit because we have an unlimited pool of (pseudo)threads to accept new connections. Second, we cannot terminate early because that would close the socket (as required by WSGI). Third, we must return an iterable to conform to WSGI.

In order to conform to the WSGI standard, all we have to do is to return a body iterable that we can write to asynchronously. With the help of `gevent.queue <http://www.gevent.org/gevent.queue.html>`_, we can *simulate* a detached socket and rewrite the previous example as follows::

    @route('/fetch')
    def fetch():
        body = gevent.queue.Queue()
        worker = SomeAsyncWorker()
        worker.on_data(lambda chunk: body.put(chunk))
        worker.on_finish(lambda: body.put(StopIteration))
        return body

From the server perspective, the queue object is iterable, blocks if empty and stops as soon as it reaches ``StopIteration``. This conforms to WSGI. On application side, the queue object behaves like a non-blocking socket. You can write to it at any time, pass it around and even start a new (pseudo)thread that writes to it asynchronously. This is how long-polling is implemented most of the time.

If the demand is high enough, I could port the `gevent long-polling chat example <https://bitbucket.org/denis/gevent/src/tip/examples/webchat/>`_ to bottle. Join the `mailing-list <mailto:bottlepy@googlegroups.com>`_ if you have questions or want to help.
