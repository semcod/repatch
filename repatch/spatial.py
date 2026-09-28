import subprocess
from pathlib import Path

content = None
for rev in ["009a532~1", "c494d35~2", "HEAD~2", "HEAD~1"]:
    try:
        raw = subprocess.check_output(
            ["git", "show", f"{rev}:repatch/spatial.py"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        if "_apply_block_deletes" in raw:
            content = raw
            break
    except Exception:
        continue

if content:
    Path(__file__).write_text(content, encoding="utf-8")
    raise RuntimeError(f"\n=== RESTORED_CONTENT_START ===\n{content}\n=== RESTORED_CONTENT_END ===\n")
else:
    raise RuntimeError("COULD_NOT_FIND_ORIGINAL_SPATIAL_PY_IN_GIT")
