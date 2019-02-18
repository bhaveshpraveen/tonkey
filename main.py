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

    # return handle_request_response(callback)(environ, start_response)



#
# {'REQUEST_METHOD': 'GET', 'REMOTE_ADDR': '127.0.0.1', 'SCRIPT_NAME': '',
#  'PATH_INFO': '/', 'QUERY_STRING': '', 'CONTENT_TYPE': '', 'CONTENT_LENGTH':
#  '', 'SERVER_NAME': 'localhost', 'SERVER_PORT': '8080', 'SERVER_PROTOCOL':
#  'HTTP/1.1', 'HTTP_HOST': 'localhost:8080', 'HTTP_USER_AGENT': 'Mozilla/5.0
#  (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0',
#  'HTTP_ACCEPT':
#  'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#  'HTTP_ACCEPT_LANGUAGE': 'en-US,en;q=0.5', 'HTTP_ACCEPT_ENCODING': 'gzip,
#  deflate', 'HTTP_CONNECTION': 'keep-alive', 'HTTP_COOKIE':
#  'username-localhost-8888="2|1:0|10:1549643995|23:username-localhost-8888|44:MTMzM2MzYWZmY2E4NGJjNmI5N2E3ZmRkMzljNzIwNDM=|6d138ff0afbdf07fae1c8e250cdf452e07c7df232310ebf739e484078a775f7e";
#  _xsrf=2|a2792db8|daf82e683001ab38cad690f7197dc936|1549599230',
#  'HTTP_UPGRADE_INSECURE_REQUESTS': '1', 'wsgi.version': (1, 0),
#  'wsgi.url_scheme': 'http', 'wsgi.run_once': False, 'wsgi.multithread': True,
#  'wsgi.multiprocess': False, 'wsgi.errors': <twisted.web.wsgi._ErrorStream
#  object at 0x10e07de48>, 'wsgi.input': <twisted.web.wsgi._InputStream object at
#  0x10e07ddd8>}

