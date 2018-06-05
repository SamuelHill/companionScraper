from http.server import BaseHTTPRequestHandler, HTTPServer
import api_python3_ahocorasick as aho
import traceback
import json
 
class HTTP_Handler(BaseHTTPRequestHandler):

  helpMessage = "Usage: \n $ curl localhost:<port>/event_interests -d '{\"faculty\":\"<name>\",\"title\":\"<title>\",\"desc\":\"<abstract>\"[,\"save_path\":\"<path/name>\"]}'\n $ curl localhost:<port>/reload\nDefault port: 8081\n"

  def _set_default_response(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

  def _interest_handling(self):
    response_txt = ''
    try:
        content_length = int(self.headers['Content-Length'])
        content = self.rfile.read(content_length).decode('utf-8')
        response_txt = aho.process_json_request(content)
    except Exception as e:
        self.send_response(400)
        traceback.print_exc()
        return str(e) + '\n'
    return response_txt

  def _reload_request(self):
    try:
        aho.reload()
        return "Done.\n"
    except Exception as e:
        return str(e) + "\nReload failed."

  def _route_request_handling(self):
    self._set_default_response()
    response = None
    if self.path == '/event_interests':
        response = self._interest_handling()
    elif self.path == '/reload':
        response = self._reload_request()
    else:
        response = HTTP_Handler.helpMessage
    self.wfile.write(bytes(response, "utf-8"))
    return

  def do_GET(self):
    self._route_request_handling()
    return

  def do_POST(self):
    self._route_request_handling()
    return

def run(server_class=HTTPServer, handler_class=HTTP_Handler, port=8081):
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