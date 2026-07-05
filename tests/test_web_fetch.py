from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import pytest

from repatch import fetch_complete_web_page


class FakeResp:
    def __init__(self, payload: bytes, *, url: str, content_type: str):
        self.headers = {"Content-Type": content_type}
        self.url = url
        self._payload = payload
        self._offset = 0

    def read(self, n=-1):
        if self._offset >= len(self._payload):
            return b""
        if n == -1:
            n = len(self._payload) - self._offset
        end = min(self._offset + max(n, 0), len(self._payload))
        chunk = self._payload[self._offset : end]
        self._offset = end
        return chunk

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_fetch_complete_web_page_mirrors_stylesheets_and_images(tmp_path):
    html = (
        b"<!DOCTYPE html><html><head>"
        b'<link rel="stylesheet" href="/styles/main.css">'
        b"</head><body>"
        b'<img src="/img/hero.png" srcset="/img/hero.png 1x, /img/hero@2x.png 2x">'
        b'<img data-src="/img/lazy.jpg" alt="Lazy">'
        b"</body></html>"
    )
    css = b"body{color:navy}"
    png = b"\x89PNG\r\n"
    jpg = b"\xff\xd8\xff"

    def fake_urlopen(req, timeout=0):
        target = req.full_url
        if target.endswith("/styles/main.css"):
            return FakeResp(css, url=target, content_type="text/css; charset=utf-8")
        if target.endswith("/img/lazy.jpg"):
            return FakeResp(jpg, url=target, content_type="image/jpeg")
        if target.endswith(".png"):
            return FakeResp(png, url=target, content_type="image/png")
        return FakeResp(html, url="https://example.com/demo", content_type="text/html; charset=utf-8")

    with patch("repatch.web_fetch._SAFE_OPENER.open", side_effect=fake_urlopen):
        result = fetch_complete_web_page(
            "https://example.com/demo",
            source_dir=tmp_path,
            render_js=False,
        )

    assert result.method == "urllib"
    assert 'href="assets/stylesheet-0.css"' in result.html
    assert 'src="assets/image-0.png"' in result.html
    assert "assets/image-1.png 2x" in result.html
    assert 'data-src="assets/image-2.jpg"' in result.html
    assert (tmp_path / "assets" / "stylesheet-0.css").is_file()
    assert len(result.assets) == 4


def test_fetch_complete_web_page_uses_rendered_dom_and_mirrors_assets(tmp_path):
    rendered_html = (
        '<html><head><link rel="stylesheet" href="/app.css"></head>'
        '<body><main id="root"><h1>Rendered</h1><img src="/hero.webp"></main></body></html>'
    )

    def fake_urlopen(req, timeout=0):
        target = req.full_url
        if target.endswith("/app.css"):
            return FakeResp(b"main{display:grid}", url=target, content_type="text/css")
        if target.endswith("/hero.webp"):
            return FakeResp(b"RIFFWEBP", url=target, content_type="image/webp")
        raise AssertionError(f"page HTML should come from Playwright, got fetch: {target}")

    with (
        patch(
            "repatch.web_fetch._render_with_playwright",
            return_value=(rendered_html, "https://example.com/app"),
        ),
        patch("repatch.web_fetch._SAFE_OPENER.open", side_effect=fake_urlopen),
    ):
        result = fetch_complete_web_page("https://example.com/app", source_dir=tmp_path)

    assert result.method == "playwright"
    assert "<h1>Rendered</h1>" in result.html
    assert 'href="assets/stylesheet-0.css"' in result.html
    assert 'src="assets/image-0.webp"' in result.html
    assert {asset.kind for asset in result.assets} == {"stylesheet", "image"}


def test_fetch_complete_web_page_falls_back_when_rendering_fails(tmp_path):
    html = b"<html><body><h1>Fallback</h1></body></html>"

    def fake_urlopen(req, timeout=0):
        return FakeResp(html, url=req.full_url, content_type="text/html; charset=utf-8")

    with (
        patch("repatch.web_fetch._render_with_playwright", side_effect=RuntimeError("browser missing")),
        patch("repatch.web_fetch._SAFE_OPENER.open", side_effect=fake_urlopen),
    ):
        result = fetch_complete_web_page("https://example.com/fallback", source_dir=tmp_path)

    assert result.method == "urllib"
    assert "browser missing" in result.render_error
    assert "<h1>Fallback</h1>" in result.html


def test_fetch_complete_web_page_deduplicates_and_skips_external_assets(tmp_path):
    html = (
        b"<html><head>"
        b'<link rel="stylesheet" href="/shared.css">'
        b'<link rel="stylesheet" href="/shared.css">'
        b'<link rel="stylesheet" href="https://cdn.example.net/theme.css">'
        b"</head><body>"
        b'<img src="/logo.png">'
        b'<img src="/logo.png">'
        b'<img src="data:image/png;base64,abc">'
        b'<img src="https://cdn.example.net/remote.png">'
        b"</body></html>"
    )

    def fake_urlopen(req, timeout=0):
        target = req.full_url
        if target.endswith("/shared.css"):
            return FakeResp(b"body{}", url=target, content_type="text/css")
        if target.endswith("/logo.png"):
            return FakeResp(b"\x89PNG\r\n", url=target, content_type="image/png")
        return FakeResp(html, url="https://example.com/", content_type="text/html")

    with patch("repatch.web_fetch._SAFE_OPENER.open", side_effect=fake_urlopen):
        result = fetch_complete_web_page(
            "https://example.com/",
            source_dir=tmp_path,
            render_js=False,
        )

    assert result.html.count("assets/stylesheet-0.css") == 2
    assert result.html.count("assets/image-0.png") == 2
    assert "https://cdn.example.net/theme.css" in result.html
    assert "https://cdn.example.net/remote.png" in result.html
    assert len(result.assets) == 2


def test_fetch_complete_web_page_rejects_non_http_urls(tmp_path):
    with pytest.raises(ValueError, match="URL must be http or https"):
        fetch_complete_web_page("file:///tmp/page.html", source_dir=tmp_path, render_js=False)


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "http://localhost/",
        "http://169.254.169.254/latest/meta-data/",  # cloud metadata endpoint
        "http://10.0.0.5/",
        "http://192.168.1.1/",
    ],
)
def test_fetch_complete_web_page_rejects_private_and_link_local_hosts(tmp_path, url):
    """SSRF guard: an attacker-supplied URL must never reach internal/loopback
    addresses, including the cloud metadata service."""
    with pytest.raises(ValueError, match="non-public address"):
        fetch_complete_web_page(url, source_dir=tmp_path, render_js=False)


def test_ssrf_redirect_handler_blocks_redirect_to_private_address():
    """A public URL that redirects to a private address must not be followed."""
    from repatch.web_fetch import _SSRFSafeRedirectHandler
    from urllib.error import URLError
    from urllib.request import Request

    handler = _SSRFSafeRedirectHandler()
    req = Request("https://example.com/")
    with pytest.raises(URLError, match="non-public address"):
        handler.redirect_request(
            req, None, 302, "Found", {}, "http://169.254.169.254/latest/meta-data/"
        )


def test_fetch_complete_web_page_against_local_http_server(tmp_path):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            routes = {
                "/": (
                    "text/html; charset=utf-8",
                    b'<!DOCTYPE html><html><head><link rel="stylesheet" href="/site.css"></head>'
                    b'<body><h1>Local page</h1><img src="/hero.png"></body></html>',
                ),
                "/site.css": ("text/css", b"h1{color:#123456}"),
                "/hero.png": ("image/png", b"\x89PNG\r\n"),
            }
            content_type, payload = routes.get(self.path, ("text/plain", b"missing"))
            self.send_response(200 if self.path in routes else 404)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format, *args):  # noqa: A002
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/"
        # This test's target is a same-machine test server, not an
        # attacker-supplied URL — bypass the SSRF private-address guard
        # (see _validate_http_url) that would otherwise (correctly) reject
        # loopback addresses for real fetch requests.
        with patch("repatch.web_fetch._non_public_ip_reason", return_value=None):
            result = fetch_complete_web_page(url, source_dir=tmp_path, render_js=False)
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert result.final_url == url
    assert "<h1>Local page</h1>" in result.html
    assert 'href="assets/stylesheet-0.css"' in result.html
    assert 'src="assets/image-0.png"' in result.html
    assert (tmp_path / "assets" / "stylesheet-0.css").read_text(encoding="utf-8") == "h1{color:#123456}"
    assert (tmp_path / "assets" / "image-0.png").read_bytes() == b"\x89PNG\r\n"


def test_fetch_complete_web_page_records_asset_errors_without_breaking_page(tmp_path):
    html = b'<html><body><h1>Partial assets</h1><img src="/missing.png"></body></html>'

    def fake_urlopen(req, timeout=0):
        target = req.full_url
        if target.endswith("/missing.png"):
            raise TimeoutError("asset timeout")
        return FakeResp(html, url="https://example.com/", content_type="text/html")

    with patch("repatch.web_fetch._SAFE_OPENER.open", side_effect=fake_urlopen):
        result = fetch_complete_web_page(
            "https://example.com/",
            source_dir=tmp_path,
            render_js=False,
        )

    assert "<h1>Partial assets</h1>" in result.html
    assert 'src="/missing.png"' in result.html
    assert result.assets == []
    assert result.errors == ["/missing.png: asset timeout"]
