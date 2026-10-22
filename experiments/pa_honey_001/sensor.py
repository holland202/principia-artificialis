#!/usr/bin/env python3
"""PA-HONEY-001 low-interaction HTTP(S) sensor. Standard library only.

It records every request it receives and always returns the same static page. It never runs, stores
for later use, or reflects anything a client sends; it makes no outbound connections. Logs are JSON
lines, one per request, with a SHA-256 of the raw request bytes as received.

Usage: sensor.py --port 80 --log /var/lib/pa-honey/http.jsonl [--tls-cert C --tls-key K] [--sensor-id S]
"""
import argparse
import base64
import hashlib
import json
import os
import socket
import ssl
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_BODY = 64 * 1024          # bytes kept per request; the rest is counted, not read
MAX_LOG_BYTES = 4 * 1024**3   # stop logging (not serving) when the log reaches 4 GiB
TIMEOUT_S = 10                # per-connection socket timeout (slow clients cannot hold threads)
MAX_THREADS = 64
PAGE = b"<!doctype html><html><head><title>Welcome</title></head><body><h1>It works</h1></body></html>\n"

_lock = threading.Lock()
_slots = threading.BoundedSemaphore(MAX_THREADS)


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Handler(BaseHTTPRequestHandler):
    server_version = "Apache"
    sys_version = ""
    protocol_version = "HTTP/1.0"   # one request per connection keeps the record simple
    timeout = TIMEOUT_S

    def log_message(self, *args):    # silence default stderr access log; we write our own
        pass

    def _record(self):
        length = self.headers.get("Content-Length", "")
        try:
            n = max(0, int(length))
        except ValueError:
            n = 0
        body, truncated = b"", False
        if n:
            try:
                body = self.rfile.read(min(n, MAX_BODY))
            except (socket.timeout, OSError):
                body = b""
            truncated = n > MAX_BODY
        raw = self.raw_requestline + bytes(self.headers) + body
        rec = {
            "schema": "pa.honey.http/1",
            "sensor": self.server.sensor_id,
            "port": self.server.server_address[1],
            "tls": self.server.tls,
            "t_utc": utc_now(),
            "src_ip": self.client_address[0],
            "src_port": self.client_address[1],
            "request_line": self.raw_requestline.decode("latin-1", "replace").rstrip("\r\n"),
            "headers": [[k, v] for k, v in self.headers.items()],
            "content_length_declared": length,
            "body_b64": base64.b64encode(body).decode("ascii"),
            "body_truncated": truncated,
            "raw_sha256": hashlib.sha256(raw).hexdigest(),
        }
        line = (json.dumps(rec, ensure_ascii=True, sort_keys=True) + "\n").encode("ascii")
        with _lock:
            try:
                if os.path.getsize(self.server.log_path) + len(line) > MAX_LOG_BYTES:
                    return
            except OSError:
                pass
            with open(self.server.log_path, "ab") as fp:
                fp.write(line)
                fp.flush()
                os.fsync(fp.fileno())

    def _reply(self, include_body=True):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(PAGE)))
        self.send_header("Connection", "close")
        self.end_headers()
        if include_body:
            self.wfile.write(PAGE)

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (socket.timeout, ConnectionError, ssl.SSLError, OSError):
            self.close_connection = True

    def _any(self):
        self._record()
        self._reply(include_body=self.command != "HEAD")

    # Every method gets the same treatment, including unknown ones.
    def __getattr__(self, name):
        if name.startswith("do_"):
            return self._any
        raise AttributeError(name)


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def process_request(self, request, client_address):
        if not _slots.acquire(blocking=False):
            request.close()           # at capacity: drop, do not queue
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            _slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            _slots.release()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--bind", default="0.0.0.0")
    ap.add_argument("--log", required=True)
    ap.add_argument("--sensor-id", default=socket.gethostname())
    ap.add_argument("--tls-cert")
    ap.add_argument("--tls-key")
    a = ap.parse_args(argv)
    srv = Server((a.bind, a.port), Handler)
    srv.log_path = a.log
    srv.sensor_id = a.sensor_id
    srv.tls = bool(a.tls_cert)
    if a.tls_cert:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(a.tls_cert, a.tls_key)
        srv.socket = ctx.wrap_socket(srv.socket, server_side=True, do_handshake_on_connect=False)
    os.makedirs(os.path.dirname(os.path.abspath(a.log)), exist_ok=True)
    print(f"PA-HONEY-001 sensor {a.sensor_id} listening on {a.bind}:{a.port} tls={srv.tls} log={a.log}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    sys.exit(main())
