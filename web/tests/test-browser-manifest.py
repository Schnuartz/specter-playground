#!/usr/bin/env python3
"""Check the exact Playground MockUI freeze inputs before the WASM build."""

import os
from pathlib import Path
import sys


source = Path(sys.argv[1]).resolve()
manifest = source / "browser.manifest.py"
tools = source / "f469-disco/micropython/tools"
sys.path.insert(0, str(tools))
import manifestfile
previous = Path.cwd()
try:
    os.chdir(source)
    parsed = manifestfile.ManifestFile(
        manifestfile.MODE_FREEZE, {"MPY_LIB_DIR": None}
    )
    parsed.execute(str(manifest))
finally:
    os.chdir(previous)

files = [Path(result.full_path) for result in parsed.files()]
if not files or any(not path.is_file() for path in files):
    raise SystemExit("Browser freeze manifest has missing Python modules")
expected = [
    source / "browser_mockui_entry/main.py",
    source / "scenarios/MockUI/src/MockUI/__init__.py",
    source / "src/app.py",
    source / "src/gui/specter.py",
]
if any(path not in files for path in expected):
    raise SystemExit("Browser freeze omitted MockUI or Specter modules")
if source / "src/main.py" in files:
    raise SystemExit("Browser freeze selected the wallet entry point instead of MockUI")
print(f"Browser freeze manifest: {len(files)} Python modules, MockUI entry point valid")
