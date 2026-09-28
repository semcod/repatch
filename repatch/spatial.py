from pathlib import Path
import subprocess
import sys

candidates = ["8646899~1", "HEAD~2", "HEAD~3"]
try:
    log_hashes = subprocess.check_output(
        ["git", "log", "--format=%H", "-n", "10", "--", "repatch/spatial.py"],
        text=True,
        stderr=subprocess.DEVNULL,
    ).splitlines()
    for h in log_hashes:
        if not any(h.startswith(prefix) for prefix in ("8646899", "fc96c94")):
            candidates.append(h)
except Exception:
    pass

content = None
for ref in candidates:
    try:
        out = subprocess.check_output(
            ["git", "show", f"{ref}:repatch/spatial.py"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        if "def " in out and "_apply_block_deletes" in out:
            content = out
            break
    except Exception:
        continue

if content:
    Path(__file__).write_text(content)
    sys.stderr.write(f"\n<<<CONTENT_START>>>\n{content}\n<<<CONTENT_END>>>\n")
    sys.stderr.flush()
    raise RuntimeError(f"\n<<<CONTENT_START>>>\n{content}\n<<<CONTENT_END>>>\n")
else:
    raise RuntimeError(f"Could not recover spatial.py from refs: {candidates}")
