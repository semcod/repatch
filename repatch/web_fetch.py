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


def _read_http_body(url: str, *, max_bytes: int = MAX_HTTP_BYTES) -> tuple[bytes, str, str, str | None]:
    err = _validate_http_url(url)
    if err:
        raise ValueError(err)
    req = Request(url.strip(), headers={"User-Agent": HTTP_USER_AGENT})
    with _SAFE_OPENER.open(req, timeout=HTTP_TIMEOUT) as resp:
        final_url = str(getattr(resp, "url", None) or url.strip())
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
    return b"".join(chunks), content_type, final_url, charset


def _render_with_playwright(url: str) -> tuple[str, str] | None:
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
            final_url = page.url or url
            status = response.status if response else 0
            browser.close()
            if status and status >= 400:
                raise ValueError(f"playwright status {status}")
            return html, final_url
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
        body, content_type, final_url, _charset = _read_http_body(
            absolute,
            max_bytes=MAX_ASSET_BYTES,
        )
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        return None, f"{original}: {exc}"[:240]
    ext = _extension_from_url_or_type(
        final_url,
        content_type,
        ".css" if kind == "stylesheet" else ".bin",
    )
    filename = f"{kind}-{index}{ext}"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / filename).write_bytes(body)
    return (
        WebAsset(
            url=final_url,
            original=original,
            local=f"assets/{filename}",
            content_type=content_type,
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


def _mirror_stylesheets(
    html: str,
    *,
    page_url: str,
    assets_dir: Path,
) -> tuple[str, list[WebAsset], list[str]]:
    assets: list[WebAsset] = []
    errors: list[str] = []
    seen: dict[str, WebAsset] = {}
    counter = 0

    def replace_link(match: re.Match[str]) -> str:
        nonlocal counter
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
        if absolute in seen:
            return _replace_attr(tag, _HREF_ATTR_RE, seen[absolute].local)
        if counter >= MAX_STYLESHEETS:
            return tag
        asset, err = _save_asset(
            absolute=absolute,
            original=href,
            kind="stylesheet",
            assets_dir=assets_dir,
            index=counter,
        )
        counter += 1
        if err:
            errors.append(err)
            return tag
        if not asset:
            return tag
        seen[absolute] = asset
        assets.append(asset)
        return _replace_attr(tag, _HREF_ATTR_RE, asset.local)

    return _LINK_TAG_RE.sub(replace_link, html), assets, errors


def _parse_srcset(value: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for item in str(value or "").split(","):
        piece = item.strip()
        if not piece:
            continue
        parts = piece.split()
        url = parts[0]
        descriptor = " ".join(parts[1:])
        out.append((url, descriptor))
    return out


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
    assets: list[WebAsset] = []
    errors: list[str] = []
    seen: dict[str, WebAsset] = {}
    counter = 0

    def mirror_url(raw: str) -> str:
        nonlocal counter
        value = raw.strip()
        if not value or value.startswith(("data:", "blob:", "javascript:")):
            return raw
        absolute = urljoin(page_url, value)
        if not _same_origin(absolute, page_url):
            return raw
        if absolute in seen:
            return seen[absolute].local
        if counter >= MAX_IMAGES:
            return raw
        asset, err = _save_asset(
            absolute=absolute,
            original=value,
            kind="image",
            assets_dir=assets_dir,
            index=counter,
        )
        counter += 1
        if err:
            errors.append(err)
            return raw
        if not asset:
            return raw
        seen[absolute] = asset
        assets.append(asset)
        return asset.local

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

    return _IMG_TAG_RE.sub(replace_img, html), assets, errors


def fetch_complete_web_page(
    url: str,
    *,
    source_dir: Path,
    render_js: bool = True,
    mirror_assets: bool = True,
) -> WebFetchResult:
    """Fetch one page, optionally render JS with Playwright, and mirror core assets locally."""
    render_error = ""
    method = "urllib"
    html = ""
    final_url = url.strip()
    content_type = "text/html; charset=utf-8"
    charset: str | None = "utf-8"

    if render_js:
        try:
            rendered = _render_with_playwright(url.strip())
            if rendered:
                html, final_url = rendered
                method = "playwright"
        except Exception as exc:
            render_error = str(exc)[:500]

    if not html:
        body, content_type, final_url, charset = _read_http_body(url.strip())
        html = _decode_http_bytes(body, content_type=content_type, charset=charset)

    assets: list[WebAsset] = []
    errors: list[str] = []
    if mirror_assets and "html" in content_type.lower():
        assets_dir = source_dir / "assets"
        html, css_assets, css_errors = _mirror_stylesheets(
            html,
            page_url=final_url,
            assets_dir=assets_dir,
        )
        html, image_assets, image_errors = _mirror_images(
            html,
            page_url=final_url,
            assets_dir=assets_dir,
        )
        assets.extend(css_assets)
        assets.extend(image_assets)
        errors.extend(css_errors)
        errors.extend(image_errors)

    return WebFetchResult(
        html=html,
        content_type=content_type,
        final_url=final_url,
        charset=charset,
        method=method,
        assets=assets,
        errors=errors,
        render_error=render_error,
    )
