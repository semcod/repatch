"""Fetch and mirror web pages for local patch workflows."""

from __future__ import annotations

import ipaddress
import mimetypes
import re
import socket
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

HTTP_TIMEOUT = 30
HTTP_USER_AGENT = "Mozilla/5.0 (compatible; repatch-web-fetch/1.0)"
MAX_HTTP_BYTES = 8_000_000
MAX_ASSET_BYTES = 1_500_000
MAX_STYLESHEETS = 12
MAX_IMAGES = 40

_CHARSET_RE = re.compile(r"charset=([^\s;]+)", re.IGNORECASE)
_LINK_TAG_RE = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
_IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_HREF_ATTR_RE = re.compile(r"""(?<![-:\w])href\s*=\s*(['"])(.*?)\1""", re.IGNORECASE)
_SRC_ATTR_RE = re.compile(r"""(?<![-:\w])src\s*=\s*(['"])(.*?)\1""", re.IGNORECASE)
_SRCSET_ATTR_RE = re.compile(r"""(?<![-:\w])srcset\s*=\s*(['"])(.*?)\1""", re.IGNORECASE)
_DATA_SRC_ATTR_RE = re.compile(r"""(?<![-:\w])data-src\s*=\s*(['"])(.*?)\1""", re.IGNORECASE)
_DATA_SRCSET_ATTR_RE = re.compile(r"""(?<![-:\w])data-srcset\s*=\s*(['"])(.*?)\1""", re.IGNORECASE)
_REL_ATTR_RE = re.compile(r"""\brel\s*=\s*(['"])(.*?)\1""", re.IGNORECASE)


@dataclass(frozen=True)
class WebAsset:
    """One mirrored page asset."""

    url: str
    original: str
    local: str
    content_type: str
    kind: str


@dataclass(frozen=True)
class WebFetchResult:
    """Fetched page HTML plus mirrored assets and diagnostics."""

    html: str
    content_type: str
    final_url: str
    charset: str | None = None
    method: str = "urllib"
    assets: list[WebAsset] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    render_error: str = ""


@dataclass(frozen=True)
class _HttpBody:
    """Raw HTTP response: payload plus where it ultimately came from."""

    payload: bytes
    content_type: str
    final_url: str
    charset: str | None


@dataclass(frozen=True)
class _PageSource:
    """Resolved page source: rendered DOM (Playwright) or raw HTTP fallback."""

    html: str
    content_type: str
    final_url: str
    charset: str | None
    method: str
    render_error: str = ""


def _non_public_ip_reason(ip_str: str) -> str | None:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return None
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local  # covers cloud metadata endpoints (169.254.169.254)
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    ):
        return f"resolves to a non-public address ({ip_str})"
    return None


def _validate_http_url(url: str) -> str | None:
    """Reject non-http(s) URLs and hosts that resolve to private/internal
    addresses (SSRF guard) — Cinema fetches externally supplied URLs
    server-side, so a loopback/link-local/RFC1918 target (including cloud
    metadata services at 169.254.169.254) must never be reachable this way.
    """
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        return "URL must be http or https"
    if not parsed.netloc:
        return "invalid URL"
    hostname = parsed.hostname
    if not hostname:
        return "invalid URL"
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        return f"could not resolve host: {exc}"
    for info in infos:
        reason = _non_public_ip_reason(info[4][0])
        if reason:
            return f"refusing to fetch {hostname}: {reason}"
    return None


class _SSRFSafeRedirectHandler(HTTPRedirectHandler):
    """Re-validate each redirect target before following it.

    Without this, an initially-valid public URL could redirect to an
    internal address and urllib would follow it transparently.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        err = _validate_http_url(newurl)
        if err:
            raise URLError(f"blocked redirect to {newurl}: {err}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_SAFE_OPENER = build_opener(_SSRFSafeRedirectHandler)


def _charset_from_content_type(content_type: str) -> str | None:
    match = _CHARSET_RE.search(content_type)
    if not match:
        return None
    return match.group(1).strip('"\'').lower() or None


def _decode_http_bytes(body: bytes, *, content_type: str, charset: str | None = None) -> str:
    encoding = charset or _charset_from_content_type(content_type) or "utf-8"
    try:
        return body.decode(encoding)
    except (LookupError, UnicodeDecodeError):
        return body.decode("utf-8", errors="replace")


def _same_origin(url: str, base_url: str) -> bool:
    left = urlparse(url)
    right = urlparse(base_url)
    return left.scheme in {"http", "https"} and left.netloc == right.netloc


def _read_http_body(url: str, *, max_bytes: int = MAX_HTTP_BYTES) -> _HttpBody:
    err = _validate_http_url(url)
    if err:
        raise ValueError(err)
    req = Request(url.strip(), headers={"User-Agent": HTTP_USER_AGENT})
    with _SAFE_OPENER.open(req, timeout=HTTP_TIMEOUT) as resp:
        content_type = str(resp.headers.get("Content-Type") or "text/html")
        charset = _charset_from_content_type(content_type)
        chunks: list[bytes] = []
        total = 0
        while True:
            block = resp.read(65536)
            if not block:
                break
            total += len(block)
            if total > max_bytes:
                raise ValueError(f"HTTP response exceeds {max_bytes} bytes")
            chunks.append(block)
    return _HttpBody(
        payload=b"".join(chunks),
        content_type=content_type,
        final_url=str(getattr(resp, "url", None) or url.strip()),
        charset=charset,
    )


def _render_with_playwright(url: str) -> _PageSource | None:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore[import-not-found]
    except Exception:
        return None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            response = page.goto(url, wait_until="networkidle", timeout=30_000)
            page.wait_for_timeout(500)
            html = page.content()
            resolved_url = page.url or url
            status = response.status if response else 0
            browser.close()
            if status and status >= 400:
                raise ValueError(f"playwright status {status}")
            return _PageSource(
                html=html,
                content_type="text/html; charset=utf-8",
                final_url=resolved_url,
                charset="utf-8",
                method="playwright",
            )
    except Exception as exc:
        raise RuntimeError(str(exc)) from exc


def _extension_from_url_or_type(url: str, content_type: str, fallback: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix and len(suffix) <= 8:
        return suffix
    guessed = mimetypes.guess_extension(content_type.split(";", 1)[0].strip())
    return guessed or fallback


def _save_asset(
    *,
    absolute: str,
    original: str,
    kind: str,
    assets_dir: Path,
    index: int,
) -> tuple[WebAsset | None, str | None]:
    try:
        asset_body = _read_http_body(
            absolute,
            max_bytes=MAX_ASSET_BYTES,
        )
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        return None, f"{original}: {exc}"[:240]
    ext = _extension_from_url_or_type(
        asset_body.final_url,
        asset_body.content_type,
        ".css" if kind == "stylesheet" else ".bin",
    )
    filename = f"{kind}-{index}{ext}"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / filename).write_bytes(asset_body.payload)
    return (
        WebAsset(
            url=asset_body.final_url,
            original=original,
            local=f"assets/{filename}",
            content_type=asset_body.content_type,
            kind=kind,
        ),
        None,
    )


def _is_stylesheet_link(tag: str) -> bool:
    rel_match = _REL_ATTR_RE.search(tag)
    return bool(rel_match and "stylesheet" in rel_match.group(2).lower())


def _replace_attr(tag: str, pattern: re.Pattern[str], value: str) -> str:
    if not pattern.search(tag):
        return tag
    return pattern.sub(lambda match: f'{match.group(0).split("=", 1)[0]}="{value}"', tag, count=1)


class _AssetMirror:
    """Own mirrored-asset bookkeeping: dedup, attempt cap, naming, asset errors."""

    def __init__(self, *, assets_dir: Path, max_assets: int) -> None:
        self._assets_dir = assets_dir
        self._max_assets = max_assets
        self._seen: dict[str, WebAsset] = {}
        self._attempts = 0
        self.assets: list[WebAsset] = []
        self.asset_errors: list[str] = []

    def mirror(self, *, absolute: str, original: str, kind: str) -> str | None:
        """Return the local URL for one asset, or None to keep the original."""
        if absolute in self._seen:
            return self._seen[absolute].local
        if self._attempts >= self._max_assets:
            return None
        asset, err = _save_asset(
            absolute=absolute,
            original=original,
            kind=kind,
            assets_dir=self._assets_dir,
            index=self._attempts,
        )
        self._attempts += 1
        if err:
            self.asset_errors.append(err)
            return None
        if not asset:
            return None
        self._seen[absolute] = asset
        self.assets.append(asset)
        return asset.local


def _mirror_stylesheets(
    html: str,
    *,
    page_url: str,
    assets_dir: Path,
) -> tuple[str, list[WebAsset], list[str]]:
    mirror = _AssetMirror(assets_dir=assets_dir, max_assets=MAX_STYLESHEETS)

    def replace_link(match: re.Match[str]) -> str:
        tag = match.group(0)
        if not _is_stylesheet_link(tag):
            return tag
        href_match = _HREF_ATTR_RE.search(tag)
        if not href_match:
            return tag
        href = href_match.group(2).strip()
        absolute = urljoin(page_url, href)
        if not _same_origin(absolute, page_url):
            return tag
        local = mirror.mirror(absolute=absolute, original=href, kind="stylesheet")
        if not local:
            return tag
        return _replace_attr(tag, _HREF_ATTR_RE, local)

    return _LINK_TAG_RE.sub(replace_link, html), mirror.assets, mirror.asset_errors


def _parse_srcset(value: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for item in str(value or "").split(","):
        piece = item.strip()
        if not piece:
            continue
        entry_fields = piece.split()
        url = entry_fields[0]
        descriptor = " ".join(entry_fields[1:])
        pairs.append((url, descriptor))
    return pairs


def _format_srcset(items: list[tuple[str, str]]) -> str:
    chunks = []
    for url, descriptor in items:
        chunks.append((url + (" " + descriptor if descriptor else "")).strip())
    return ", ".join(chunks)


def _mirror_images(
    html: str,
    *,
    page_url: str,
    assets_dir: Path,
) -> tuple[str, list[WebAsset], list[str]]:
    mirror = _AssetMirror(assets_dir=assets_dir, max_assets=MAX_IMAGES)

    def mirror_url(raw: str) -> str:
        value = raw.strip()
        if not value or value.startswith(("data:", "blob:", "javascript:")):
            return raw
        absolute = urljoin(page_url, value)
        if not _same_origin(absolute, page_url):
            return raw
        local = mirror.mirror(absolute=absolute, original=value, kind="image")
        return local or raw

    def replace_img(match: re.Match[str]) -> str:
        tag = match.group(0)
        src_match = _SRC_ATTR_RE.search(tag)
        if src_match:
            tag = _replace_attr(tag, _SRC_ATTR_RE, mirror_url(src_match.group(2)))
        data_src_match = _DATA_SRC_ATTR_RE.search(tag)
        if data_src_match:
            local = mirror_url(data_src_match.group(2))
            tag = _replace_attr(tag, _DATA_SRC_ATTR_RE, local)
            if not _SRC_ATTR_RE.search(tag):
                tag = tag[:-1] + f' src="{local}">'
        for pattern in (_SRCSET_ATTR_RE, _DATA_SRCSET_ATTR_RE):
            srcset_match = pattern.search(tag)
            if not srcset_match:
                continue
            mirrored = [(mirror_url(url), desc) for url, desc in _parse_srcset(srcset_match.group(2))]
            tag = _replace_attr(tag, pattern, _format_srcset(mirrored))
        return tag

    return _IMG_TAG_RE.sub(replace_img, html), mirror.assets, mirror.asset_errors


def _fetch_page_source(url: str, render_js: bool) -> _PageSource:
    """Fetch page HTML via Playwright render or raw HTTP fallback."""
    render_error = ""
    if render_js:
        try:
            rendered = _render_with_playwright(url.strip())
            if rendered and rendered.html:
                return rendered
        except Exception as exc:
            render_error = str(exc)[:500]

    http_body = _read_http_body(url.strip())
    return _PageSource(
        html=_decode_http_bytes(
            http_body.payload,
            content_type=http_body.content_type,
            charset=http_body.charset,
        ),
        content_type=http_body.content_type,
        final_url=http_body.final_url,
        charset=http_body.charset,
        method="urllib",
        render_error=render_error,
    )


def _mirror_page_assets(
    html: str,
    page_url: str,
    source_dir: Path,
) -> tuple[str, list[WebAsset], list[str]]:
    """Mirror stylesheets and images into source_dir/assets."""
    assets: list[WebAsset] = []
    mirror_errors: list[str] = []
    assets_dir = source_dir / "assets"
    html, css_assets, css_errors = _mirror_stylesheets(
        html,
        page_url=page_url,
        assets_dir=assets_dir,
    )
    html, image_assets, image_errors = _mirror_images(
        html,
        page_url=page_url,
        assets_dir=assets_dir,
    )
    assets.extend(css_assets)
    assets.extend(image_assets)
    mirror_errors.extend(css_errors)
    mirror_errors.extend(image_errors)
    return html, assets, mirror_errors


def fetch_complete_web_page(
    url: str,
    *,
    source_dir: Path,
    render_js: bool = True,
    mirror_assets: bool = True,
) -> WebFetchResult:
    """Fetch one page, optionally render JS with Playwright, and mirror core assets locally."""
    source = _fetch_page_source(url, render_js)

    html = source.html
    assets: list[WebAsset] = []
    mirror_errors: list[str] = []
    if mirror_assets and "html" in source.content_type.lower():
        html, assets, mirror_errors = _mirror_page_assets(html, source.final_url, source_dir)

    return WebFetchResult(
        html=html,
        content_type=source.content_type,
        final_url=source.final_url,
        charset=source.charset,
        method=source.method,
        assets=assets,
        errors=mirror_errors,
        render_error=source.render_error,
    )
