from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class FixtureHandler(BaseHTTPRequestHandler):
    last_authorization = None

    def log_message(self, format, *args):
        return

    def _send(self, status, payload):
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        type(self).last_authorization = self.headers.get("Authorization")
        if self.path == "/v1/health":
            self._send(200, {"status": "ok", "version": "fixture-1.0"})
        elif self.path == "/v1/models":
            self._send(200, {"object": "list", "data": [{"id": "Fixture-Model", "downloaded": True, "recipe": "fixture"}]})
        elif self.path == "/v1/stats":
            self._send(200, {
                "time_to_first_token": 0.25,
                "tokens_per_second": 42.0,
                "input_tokens": 12,
                "output_tokens": 5,
            })
        elif self.path == "/v1/system-stats":
            self._send(200, {
                "cpu_percent": 12.5,
                "memory_gb": 8.0,
                "gpu_percent": 44.0,
                "vram_gb": 2.25,
                "npu_percent": 7.0,
            })
        elif self.path == "/v1/system-info":
            self._send(200, {"os": "fixture-os", "devices": ["fixture-device"]})
        else:
            self._send(404, {"error": {"message": "not found"}})

    def do_POST(self):
        type(self).last_authorization = self.headers.get("Authorization")
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/v1/chat/completions":
            if payload.get("model") == "Error-Model":
                self._send(500, {"error": {"message": "fixture inference failure"}})
                return
            self._send(200, {"id": "fixture-completion", "choices": [{"message": {"role": "assistant", "content": "fixture response"}}]})
        else:
            self._send(404, {"error": {"message": "not found"}})


@contextmanager
def fixture_server():
    FixtureHandler.last_authorization = None
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", FixtureHandler
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
