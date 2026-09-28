"""Tests for repatch.dom_patch."""

from repatch.dom_patch import (
    build_function_option_patches,
    build_function_patch_context,
    supports_function_patch,
)


def test_supports_function_patch():
    assert supports_function_patch("functions", "imported") is True
    assert supports_function_patch("functions", "web") is True
    assert supports_function_patch("functions", "frontend") is True
    assert supports_function_patch("functions", "dashboard") is True
    assert supports_function_patch("functions", "slice") is True
    assert supports_function_patch("functions", "unknown") is False
    assert supports_function_patch("style", "web") is False
    assert supports_function_patch("", "web") is False


def test_build_function_patch_context():
    html_text = "<!DOCTYPE html><html><head><title>Test App</title></head><body><h1>Hello</h1></body></html>"
    context = build_function_patch_context(html_text, user_goal="Improve checkout flow")
    assert "FUNCTION PATCH IR" in context
    assert "user_goal: Improve checkout flow" in context


def test_build_function_patch_context_default_goal():
    html_text = "<html><body><div>Content</div></body></html>"
    context = build_function_patch_context(html_text)
    assert "user_goal: (none)" in context


def test_build_function_option_patches_unsupported():
    files, labels, meta = build_function_option_patches(
        "<html><body></body></html>",
        project_kind="unknown_kind",
    )
    assert files == {}
    assert labels == []
    assert meta["status"] == "unsupported"


def test_build_function_option_patches_success():
    sample_html = """<!DOCTYPE html>
<html>
<head><title>Landing Page</title></head>
<body>
  <h1>Welcome</h1>
  <button id="cta-button">Click here</button>
  <a href="#about" id="about-link">About</a>
</body>
</html>"""
    files, labels, meta = build_function_option_patches(
        sample_html,
        user_goal="Increase conversion",
        project_kind="web",
        delete_els=["cta-button"],
    )
    assert meta["status"] == "ok"
    assert len(labels) == 3
    assert "alt_a.html" in files
    assert "alt_b.html" in files
    assert "alt_c.html" in files

    for doc in files.values():
        assert "nexu-function-patch" in doc
        assert "nexu-function-evolution" in doc
