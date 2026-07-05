from pathlib import Path

from repatch import (
    enforce_deletes_on_option_previews,
    html_files_distinct,
    replace_html_title,
    sync_option_previews_from_workspace,
)


def test_replace_html_title_preserves_body() -> None:
    html = "<html><head><title>Old</title></head><body><button>7</button></body></html>"
    assert "<title>New</title>" in replace_html_title(html, "New")
    assert "<button>7</button>" in replace_html_title(html, "New")


def test_sync_option_previews_from_workspace_applies_delete_ids(tmp_path: Path) -> None:
    html = """<!DOCTYPE html><html><head><title>Base</title></head><body>
    <div class="btn btn-sci" id="btn-sin">sin</div>
    <div class="btn btn-sci" id="btn-cos">cos</div>
    </body></html>"""
    (tmp_path / "stage0.html").write_text(html, encoding="utf-8")

    result = sync_option_previews_from_workspace(
        tmp_path,
        stage=0,
        delete_ids=["cos"],
        finalize_html=lambda value: value,
    )

    assert result["status"] == "options_synced_from_workspace"
    assert "cos" in result["spatial_removed"]
    assert "btn-cos" not in (tmp_path / "alt_a.html").read_text(encoding="utf-8")
    assert (tmp_path / "stage1.html").exists()
    assert (tmp_path / "stage2.html").exists()


def test_sync_option_previews_mirrors_custom_option_files_into_stages(tmp_path: Path) -> None:
    """stage1/stage2 must mirror whichever files `option_files` actually names,
    not a hardcoded alt_b.html/alt_c.html that a custom tuple wouldn't write."""
    html = "<!DOCTYPE html><html><head><title>Base</title></head><body></body></html>"
    (tmp_path / "stage0.html").write_text(html, encoding="utf-8")
    custom_files = (
        ("custom_a.html", "Custom A"),
        ("custom_b.html", "Custom B"),
        ("custom_c.html", "Custom C"),
    )

    result = sync_option_previews_from_workspace(
        tmp_path,
        stage=0,
        delete_ids=[],
        finalize_html=lambda value: value,
        option_files=custom_files,
    )

    assert result["files"] == ["custom_a.html", "custom_b.html", "custom_c.html"]
    assert (tmp_path / "stage1.html").read_text(encoding="utf-8") == (
        tmp_path / "custom_b.html"
    ).read_text(encoding="utf-8")
    assert (tmp_path / "stage2.html").read_text(encoding="utf-8") == (
        tmp_path / "custom_c.html"
    ).read_text(encoding="utf-8")


def test_sync_option_previews_uses_delete_resolver_only_for_none(tmp_path: Path) -> None:
    html = """<!DOCTYPE html><html><body>
    <div class="btn" id="btn-a">a</div><div class="btn" id="btn-b">b</div>
    </body></html>"""
    (tmp_path / "stage0.html").write_text(html, encoding="utf-8")

    result = sync_option_previews_from_workspace(
        tmp_path,
        delete_ids=[],
        delete_resolver=lambda: ["a"],
    )

    assert result["spatial_removed"] == []
    assert "btn-a" in (tmp_path / "alt_a.html").read_text(encoding="utf-8")


def test_enforce_deletes_on_option_previews(tmp_path: Path) -> None:
    html = """<!DOCTYPE html><html><body>
    <div class="btn" id="btn-a">a</div><div class="btn" id="btn-b">b</div>
    </body></html>"""
    for name in ("alt_a.html", "alt_b.html", "alt_c.html"):
        (tmp_path / name).write_text(html, encoding="utf-8")

    result = enforce_deletes_on_option_previews(tmp_path, ["b"])

    assert result["status"] == "options_patched"
    assert "b" in result["spatial_removed"]
    assert "btn-b" not in (tmp_path / "alt_b.html").read_text(encoding="utf-8")


def test_html_files_distinct_ignores_title(tmp_path: Path) -> None:
    for name, title in (("a.html", "A"), ("b.html", "B"), ("c.html", "C")):
        (tmp_path / name).write_text(
            f"<html><head><title>{title}</title></head><body>same</body></html>",
            encoding="utf-8",
        )

    assert not html_files_distinct(tmp_path, ["a.html", "b.html", "c.html"])
    (tmp_path / "c.html").write_text(
        "<html><head><title>C</title></head><body>different</body></html>",
        encoding="utf-8",
    )
    assert html_files_distinct(tmp_path, ["a.html", "b.html", "c.html"])
