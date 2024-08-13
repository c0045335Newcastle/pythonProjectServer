# # Python 3
# from http.server import HTTPServer, SimpleHTTPRequestHandler
# import ssl
#
#
#
#
# server_address = ('localhost', 8000)
# httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
#
# httpd.socket = ssl.wrap_socket(httpd.socket,
#                                server_side=True,
#                                certfile='cert.pem',
#                                keyfile='key.pem',
#                                ssl_version=ssl.PROTOCOL_TLS)
#
# print('Serving HTTPS on localhost port 8000...')
# httpd.serve_forever()

import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl

class RequestHandlerWithLogging(SimpleHTTPRequestHandler):
    def do_GET(self):
        logging.info(f"GET request,\nPath: {str(self.path)}\nHeaders:\n{str(self.headers)}")
        super().do_GET()


logging.basicConfig(level=logging.INFO)


server_address = ('localhost', 8080)
httpd = HTTPServer(server_address, RequestHandlerWithLogging)

httpd.socket = ssl.wrap_socket(httpd.socket,
                               server_side=True,
                               certfile='cert.pem',
                               keyfile='key.pem',
                               ssl_version=ssl.PROTOCOL_TLS)

logging.info('Serving HTTPS on localhost port 8080...')
httpd.serve_forever()