# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- `apply_spatial_deletes_to_html`: the selectable-block matcher used a non-greedy
  `.*?</tag>` regex with a same-tag backreference, so a deletable block containing a
  nested tag of the *same* name (e.g. a plain `<div>` icon wrapper inside a
  `<div class="kpi-card">`) matched only up to the *inner* closing tag — a "successful"
  delete left the outer tag's remaining content and an orphaned closing tag behind,
  corrupting the option preview HTML. Replaced with a nesting-depth-tracking scanner
  (`_find_matching_close`) that finds the true matching closing tag regardless of
  same-name nesting.
- `_selectable_block_attrs` only recognized `id="btn-..."` for button-like elements, so
  a `.btn` div with nested markup (e.g. `<div class="btn" id="save"><span>Save</span></div>`)
  — which also never matches the plain-button regex, since that requires no nested tags —
  silently produced zero delete candidates: a delete request for such an element did
  nothing, with no error surfaced. Now also recognizes a `class="...btn..."` token.
- `replace_html_title` interpolated the title directly into a `re.sub` *replacement
  string*, so a title containing `\1`, `\g<name>`, or similar raised `re.error` (the
  pattern has no capturing groups) instead of being inserted literally. Fixed by using a
  replacement function, which is not subject to backslash-sequence interpretation.
- `sync_option_previews_from_workspace` mirrored options B/C into `stage1.html`/
  `stage2.html` by hardcoded `alt_b.html`/`alt_c.html` filenames regardless of the
  caller-supplied `option_files` tuple — a caller passing custom filenames would read
  stale/nonexistent default files instead of the ones just written. Now mirrors by
  position in `option_files`.
- **SSRF**: `_validate_http_url` only checked the URL scheme and a non-empty host —
  no check against loopback/link-local/private/reserved address ranges (including the
  `169.254.169.254` cloud metadata endpoint), and `urlopen` followed redirects
  transparently with no re-validation of the redirect target. Since Cinema fetches
  externally-supplied URLs server-side into the workspace, this was a real SSRF
  exposure. Fixed with hostname resolution + `ipaddress`-based private/reserved-range
  rejection, plus a custom `HTTPRedirectHandler` that re-validates every redirect hop
  before following it.
  Verified: full test suite (71 tests, +10 new/updated) passes, including new
  regression tests for nested-same-tag blocks, nested-markup buttons, custom
  `option_files`, and rejection of loopback/private/link-local/metadata URLs plus
  a redirect-to-private-address attempt.

## [0.2.19] - 2026-07-05

### Docs
- Update CHANGELOG.md
- Update README.md

### Test
- Update tests/test_options.py
- Update tests/test_spatial.py
- Update tests/test_web_fetch.py

### Other
- Update local.dev.txt
- Update repatch/options.py
- Update repatch/spatial.py
- Update repatch/web_fetch.py
- Update uv.lock

## [0.2.18] - 2026-06-29

### Docs
- Update README.md

## [0.2.17] - 2026-06-01

### Docs
- Update README.md

## [0.2.16] - 2026-06-01

### Docs
- Update README.md

## [0.2.15] - 2026-06-01

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Other
- Update .koru/event-store.jsonl
- Update .koru/events/observability.jsonl
- Update .koru/history.jsonl
- Update .koru/onboarding.json
- Update .planfile/.koru/operator-steps/mcp_koru.ticket
- Update .planfile/.koru/operator-steps/self_control.ticket
- Update .planfile/.koru/queue-runner.lock
- Update .planfile/config.yaml
- Update .planfile/sprints/current.yaml
- Update app.doql.less
- ... and 21 more files

## [0.2.14] - 2026-06-01

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md

### Test
- Update tests/test_organize_html.py
- Update tests/test_web_fetch.py
- Update tests/test_web_preprocess.py

### Other
- Update VERSION
- Update app.doql.less
- Update project/calls.png
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/flow.png
- Update project/index.html
- Update project/logic.pl
- Update project/map.toon.yaml
- Update project/project.toon.yaml
- ... and 6 more files

## [0.2.12] - 2026-06-01

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_marked_context.py
- Update tests/test_web_preprocess.py

### Other
- Update VERSION
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- ... and 17 more files

## [0.2.8] - 2026-06-01

### Docs
- Update README.md

### Test
- Update tests/test_marked_context.py

### Other
- Update VERSION
- Update repatch/__init__.py
- Update repatch/marked_context.py
- Update repatch/scope.py
- Update uv.lock

## [0.2.6] - 2026-06-01

### Docs
- Update README.md

### Test
- Update tests/test_marked_context.py

### Other
- Update repatch/__init__.py
- Update repatch/marked_context.py
- Update repatch/scope.py

## [0.2.5] - 2026-06-01

### Docs
- Update README.md

## [0.2.4] - 2026-06-01

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_options.py

### Other
- Update VERSION
- Update app.doql.less
- Update deps.json
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- ... and 18 more files

## [0.2.2] - 2026-06-01

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Test
- Update testql-scenarios/generated-cli-tests.testql.toon.yaml
- Update testql-scenarios/generated-from-pytests.testql.toon.yaml
- Update tests/test_marked_context.py

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 12 more files

## [0.2.1] - 2026-06-01

### Docs
- Update README.md
- Update TODO/1.md

### Test
- Update tests/test_dom_patch.py
- Update tests/test_marked_context.py
- Update tests/test_spatial.py
- Update tests/test_ui_patch.py

### Other
- Update VERSION
- Update repatch/__init__.py
- Update repatch/css.py
- Update repatch/dom_patch.py
- Update repatch/marked_context.py
- Update repatch/project_ir.py
- Update repatch/scope.py
- Update repatch/spatial.py
- Update repatch/ui_patch.py
- Update uv.lock

## [0.1.1] - 2026-06-01

### Docs
- Update README.md

### Other
- Update .gitignore
- Update project.sh
- Update tree.sh
- Update uv.lock

