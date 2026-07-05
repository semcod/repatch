from repatch import apply_spatial_deletes_to_html


def test_apply_spatial_deletes_removes_dashboard_kpi_card():
    html = """<!DOCTYPE html><html><body>
    <section class="kpi-card nexu-selectable" id="btn-GET" data-nexu-target="GET">
        <span>Get</span><strong>2.1k</strong></section>
    <section class="kpi-card nexu-selectable" id="btn-POST" data-nexu-target="POST">
        <span>Post</span><strong>38 ms</strong></section>
    </body></html>"""
    patched, removed = apply_spatial_deletes_to_html(html, ["GET"])
    assert "btn-GET" not in patched
    assert "btn-POST" in patched
    assert removed


def test_apply_spatial_deletes_removes_only_marked_buttons():
    html = """<!DOCTYPE html><html><body><div class="grid">
    <div class="btn btn-sci" id="btn-sin">sin</div>
    <div class="btn btn-sci-excess" id="btn-Mod">Mod</div>
    <div class="btn btn-sci-excess" id="btn-deg">deg</div>
    <div class="btn btn-sci-excess" id="btn-rad">rad</div>
    <div class="btn btn-sci-excess" id="btn-pi">π</div>
    </div></body></html>"""
    base = html
    patched, removed = apply_spatial_deletes_to_html(base, ["Mod", "deg", "rad"])
    assert set(removed) == {"Mod", "deg", "rad"}
    assert "btn-Mod" not in patched and "btn-deg" not in patched and "btn-rad" not in patched
    assert "btn-sin" in patched and "btn-pi" in patched


def test_apply_spatial_deletes_handles_nested_same_tag_block():
    """A deletable block containing a nested <div> of the same tag name must
    be removed in full — a naive non-greedy regex match stops at the first
    (inner) closing tag, leaving the outer tag's remainder as orphaned markup."""
    html = (
        '<div class="kpi-card" id="card-1">'
        '<div class="icon">X</div><span>Revenue</span>'
        "</div>"
    )
    patched, removed = apply_spatial_deletes_to_html(html, ["card-1"])
    assert removed == ["card-1"]
    assert patched == ""


def test_apply_spatial_deletes_keeps_sibling_block_after_nested_delete():
    html = (
        '<div class="dashboard">'
        '<div class="kpi-card" id="card-keep"><span>Keep me</span></div>'
        '<div class="kpi-card" id="card-remove"><span>Remove me</span></div>'
        "</div>"
    )
    patched, removed = apply_spatial_deletes_to_html(html, ["card-remove"])
    assert removed == ["card-remove"]
    assert "card-keep" in patched
    assert "card-remove" not in patched


def test_apply_spatial_deletes_removes_button_with_nested_markup():
    """A .btn div with a nested label span never matches the plain-button
    regex (which requires no nested tags); it must still be removable via
    the class="...btn..." fallback in _selectable_block_attrs."""
    html = '<div class="btn primary" id="save"><span>Save</span></div>'
    patched, removed = apply_spatial_deletes_to_html(html, ["save"])
    assert removed == ["save"]
    assert patched == ""
