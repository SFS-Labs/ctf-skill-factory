#!/usr/bin/env python3
"""Evaluator-only read-only BSC JSON-RPC proxy with conservative rate limits."""
from __future__ import annotations
import json
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

URLS = (
    "https://bsc-mainnet.public.blastapi.io",
    "https://bnb-mainnet.g.alchemy.com/public",
)
_lock = threading.Lock()
_cache: dict[str, dict] = {}
_next_time = {u: 0.0 for u in URLS}
_count = 0
_calls = 0


def upstream(method: str, params: list) -> dict:
    global _count, _calls
    if method.lower().startswith("eth_send") or method in (
        "personal_sendTransaction", "eth_signTransaction",
    ):
        return {"error": {"code": -32601, "message": "Write methods disabled on the historical read-only proxy"}}
    key = json.dumps([method, params], sort_keys=True, separators=(",", ":"))
    with _lock:
        if key in _cache:
            return dict(_cache[key])
        for attempt in range(6):
            if _calls >= 1600:
                return {"error": {"code": -32030, "message": "Evaluator read budget exhausted"}}
            url = URLS[_count % len(URLS)]
            _count += 1
            wait = _next_time[url] - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            _next_time[url] = time.monotonic() + 0.46
            payload = json.dumps({"jsonrpc": "2.0", "id": 1,
                                  "method": method, "params": params}).encode()
            req = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/json", "User-Agent": "SFS-readonly-archive-eval"})
            _calls += 1
            try:
                with urllib.request.urlopen(req, timeout=12) as response:
                    out = json.load(response)
            except (urllib.error.URLError, TimeoutError, ValueError) as error:
                print("UPSTREAM_ERROR", method, url, type(error).__name__, str(error)[:100], flush=True)
                time.sleep(0.7)
                continue
            err = out.get("error", {})
            if isinstance(err, dict) and (
                err.get("code") in (-32097, -32005, 429)
                or "rate limit" in str(err).lower()
            ):
                print("RATE_LIMIT", method, url, flush=True)
                time.sleep(0.7)
                continue
            result = {"result": out["result"]} if "result" in out else {"error": out.get("error", {})}
            if "result" in result:
                _cache[key] = result
            return result
        return {"error": {"code": -32029, "message": "Public archive upstream rate-limited on both endpoints"}}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = b"OK"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > 250000:
                raise ValueError("Invalid request size")
            obj = json.loads(self.rfile.read(size))
            if isinstance(obj, list):
                msgs = obj
            elif isinstance(obj, dict):
                msgs = [obj]
            else:
                raise ValueError("Invalid JSON-RPC payload")
            if len(msgs) > 100:
                raise ValueError("Too many requests in batch")
            outs = []
            for msg in msgs:
                if not isinstance(msg, dict) or not isinstance(msg.get("method"), str):
                    raise ValueError("Missing JSON-RPC method")
                result = upstream(msg["method"], msg.get("params", []))
                outs.append({"jsonrpc": "2.0", "id": msg.get("id"), **result})
            result_obj = outs if isinstance(obj, list) else outs[0]
            data = json.dumps(result_obj).encode()
            self.send_response(200)
        except Exception as err:
            data = json.dumps({"jsonrpc": "2.0", "id": None,
                               "error": {"code": -32700, "message": str(err)}}).encode()
            self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    print("Starting evaluator-only rate-limited BSC archive proxy", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 18546), Handler).serve_forever()
