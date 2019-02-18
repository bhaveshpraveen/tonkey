import importlib
import os
import re
import http.client
import urllib
import string
from wsgiref.headers import Headers


class NotFound(Exception):
    pass


class Request:
    def __init__(self, environ):
        self.environ = environ
        self.path = self.environ.get('PATH_INFO', '/')

    @property
    def GET(self):
        get_args = urllib.parse.parse_qs(self.environ['QUERY_STRING'])
        return {k: v for k, v in get_args.items()}


class Response:
    def __init__(self, response=None, status=200, content_type='text/html', charset='utf-8'):
        self.response = response
        self.status = status
        self.content_type = content_type
        self.charset = charset
        self.headers = Headers()
        self.headers.add_header('content-type', self.ctype)


    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        status_message = http.client.responses.get(status, 'UNKNOWN')
        self._status = f'{status} {status_message}'

    @property
    def ctype(self):
        return f'{self.content_type}; charset={self.charset}'

    def __iter__(self):
        for val in self.response:
            if isinstance(val, bytes):
                yield val
            yield val.encode(self.charset)


class Router:
    def __init__(self):
        self.router_table = []

    def add_route(self, pattern, callback):
        self.router_table.append((pattern, callback))

    def match(self, path):
        for pattern, callback in self.router_table:
            m = re.match(pattern, path)
            if m:
                return callback, m.groups()
        raise NotFound()

    def __add__(self, other):
        if not isinstance(other, Router):
            raise TypeError('Incompatible type. Must be of type \`str\` or type {}'.format(type(Router).__name__))

        for router in other:
            self.router_table.append(router)


class TemplateResponse(Response):
    def __init__(self, html, context, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(os.getcwd())
        self.template = string.Template(open(html).read())
        self.response = self.template.safe_substitute(context)

    def __iter__(self):
        yield self.response.encode(self.charset)


def application(environ, start_response):
    module = os.environ['TONKEY_APP']
    module = importlib.import_module(module)
    routes = getattr(module, 'router')

    try:
        request = Request(environ)
        callback, args = routes.match(request.path)
        response = callback(request, *args)
    except NotFound:
        response = """
            <h1>Not Found</h1>
        """
        response = Response(response=response, status=404)

    start_response(response.status, response.headers.items())
    return iter(response)


