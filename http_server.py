import http.server
import os
import socketserver

PORT = 8001
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_GET(self):
        if self.path == "/":
            self.path = "/websocket_test.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


print(f"Starting HTTP server on port {PORT}")
print(f"Serving files from: {DIRECTORY}")
print(f"Open http://localhost:{PORT} in your browser")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()
        httpd.server_close()
        print("Server stopped")
