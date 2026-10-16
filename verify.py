"""Verify the fixed publication manifest and execute every documented test suite."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def main() -> int:
    manifest = json.loads((ROOT / "PUBLICATION.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        relative = Path(entry["path"])
        path = ROOT / relative
        if relative.is_absolute() or ".." in relative.parts or not path.resolve().is_relative_to(ROOT):
            raise ValueError("Manifest path escapes the publication")
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing or unsupported source file: {relative}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"Publication file changed: {relative}")
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node 22 or newer is required; no test was silently skipped")
    java, javac = shutil.which("java"), shutil.which("javac")
    if not java or not javac:
        raise RuntimeError("A JDK 17 or newer must be on PATH; no Java check was silently skipped")
    commands = [
        ("observer8", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("operations", [node, "--test", "paid-call-control.test.mjs"]),
        ("operations", [sys.executable, "-m", "unittest", "-v", "test_career_controls.py"]),
        ("creative-tools", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("evidence-gates", [node, "--test", "availability.test.mjs"]),
    ]
    for folder, command in commands:
        print(f"\nVerifying {folder}", flush=True)
        subprocess.run(command, cwd=ROOT / folder, check=True, timeout=180)
    with tempfile.TemporaryDirectory(prefix="mekreflect-java-") as build:
        sources = [str(ROOT / "telemetry-parser" / name) for name in ("ObdParser.java", "ParserTest.java", "ParserDemo.java")]
        subprocess.run([javac, "-d", build, *sources], check=True, timeout=60)
        subprocess.run([java, "-cp", build, "com.mekreflect.carscan.ParserTest"], check=True, timeout=30)
    print(f"PASS: {len(manifest['files'])} manifest hashes and all five labs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
