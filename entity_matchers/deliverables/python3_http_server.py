'''
Querying: 
curl -X POST -d "<Faculty Name|||Event Title|||Event Description> localhost:8081"
'''

from http.server import BaseHTTPRequestHandler, HTTPServer
import api_python3_ahocorasick as aho

class pythonHTTPServer_RequestHandler(BaseHTTPRequestHandler):

  automations = aho.setup_automations(True)
  matchedFacultyInterests = aho.setup_faculty_interests(automations)

  def _set_response(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

  def _create_response_message(self):
    content_length = 0
    if self.headers['Content-Length']:
      content_length = int(self.headers['Content-Length'])

    array = self.rfile.read(content_length).decode('utf-8').split('|||')
    response_txt = ''
    if len(array) == 3:
      response_txt = aho.get_meld_string(self.automations, self.matchedFacultyInterests, False, array[0], array[1], array[2])
    return response_txt

  def do_GET(self):
    self._set_response()
    self.wfile.write(bytes(self._create_response_message(), "utf-8"))
    return

  def do_POST(self):
    self._set_response()
    self.wfile.write(bytes(self._create_response_message(), "utf-8"))
    return

def run(server_class=HTTPServer, handler_class=pythonHTTPServer_RequestHandler, port=8081):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting python-side server at %d...' % (port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('\nPython-side server stopped.')

if __name__ == '__main__':
    from sys import argv
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()