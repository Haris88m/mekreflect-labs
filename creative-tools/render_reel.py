#!/usr/bin/env python3
"""Render approved images into a silent MP4 using camera motion and fades.

The script performs only camera animation (zoom/pan) and fades. It does not
redraw, regenerate, retouch, caption, or otherwise alter story content.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

ROOT = Path(__file__).resolve().parent
DEFAULT_ARTWORK = ROOT / "example-output" / "images"
DEFAULT_CONFIG = ROOT / "example.json"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def natural_key(path: Path):
    return [int(x) if x.isdigit() else x.lower() for x in re.split(r"(\d+)", path.name)]


def discover_images(folder: Path) -> list[Path]:
    images = [p for p in folder.iterdir() if p.is_file() and not p.is_symlink() and p.suffix.lower() in EXTENSIONS]
    return sorted(images, key=natural_key)


def validate_config(cfg: dict) -> dict:
    """Reject invalid render requests before creating files or invoking FFmpeg."""
    if not isinstance(cfg, dict):
        raise ValueError("format must be an object")
    result = dict(cfg)
    for key, low, high in (("width", 16, 4096), ("height", 16, 4096), ("fps", 1, 60)):
        value = result.get(key)
        if type(value) is not int or not low <= value <= high:
            raise ValueError(f"{key} must be an integer between {low} and {high}")
    if result["width"] % 2 or result["height"] % 2:
        raise ValueError("width and height must be even for yuv420p")
    for key in ("scene_seconds", "fade_seconds"):
        value = result.get(key)
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"{key} must be a finite number")
    if not 0 < result["scene_seconds"] <= 60:
        raise ValueError("scene_seconds must be greater than zero and at most 60")
    if not 0 <= result["fade_seconds"] <= result["scene_seconds"] / 2:
        raise ValueError("fade_seconds must be between zero and half a scene")
    if result.get("video_codec", "libx264") != "libx264":
        raise ValueError("only libx264 is supported")
    if result.get("pixel_format", "yuv420p") != "yuv420p":
        raise ValueError("only yuv420p is supported")
    if result.get("audio", False) is not False:
        raise ValueError("this renderer does not support audio")
    return result


def validate_image(path: Path) -> tuple[int, int]:
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        return im.size


def motion_filter(index: int, fps: int, seconds: float, width: int, height: int, fade: float) -> str:
    frames = max(1, int(round(seconds * fps)))
    fade_out_start = max(0.0, seconds - fade)

    patterns = [
        ("min(zoom+0.00033,1.060)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
        ("min(zoom+0.00028,1.050)", "(iw-iw/zoom)*(on/%d)" % max(frames - 1, 1), "ih/2-(ih/zoom/2)"),
        ("min(zoom+0.00028,1.050)", "(iw-iw/zoom)*(1-on/%d)" % max(frames - 1, 1), "ih/2-(ih/zoom/2)"),
        ("min(zoom+0.00030,1.055)", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(1-on/%d)" % max(frames - 1, 1)),
    ]
    z, x, y = patterns[index % len(patterns)]

    return (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={width}x{height}:fps={fps},"
        f"fade=t=in:st=0:d={fade:.3f},"
        f"fade=t=out:st={fade_out_start:.3f}:d={fade:.3f},"
        "format=yuv420p"
    )


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def render_scene(ffmpeg: str, image: Path, out: Path, index: int, cfg: dict) -> None:
    width = int(cfg["width"])
    height = int(cfg["height"])
    fps = int(cfg["fps"])
    seconds = float(cfg["scene_seconds"])
    fade = float(cfg["fade_seconds"])
    vf = motion_filter(index, fps, seconds, width, height, fade)

    cmd = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
        "-loop", "1", "-i", str(image),
        "-vf", vf,
        "-t", f"{seconds:.3f}",
        "-r", str(fps),
        "-an",
        "-c:v", cfg.get("video_codec", "libx264"),
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", cfg.get("pixel_format", "yuv420p"),
        "-movflags", "+faststart",
        str(out),
    ]
    run(cmd)


def concat_scenes(ffmpeg: str, scenes: list[Path], output: Path) -> None:
    list_file = output.parent / "concat.txt"
    with list_file.open("w", encoding="utf-8") as f:
        for scene in scenes:
            safe = scene.resolve().as_posix().replace("'", "'\\''")
            f.write(f"file '{safe}'\n")

    cmd = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy",
        "-movflags", "+faststart",
        str(output),
    ]
    run(cmd)
    list_file.unlink(missing_ok=True)


def render(artwork: Path, cfg: dict, output: Path) -> dict:
    cfg = validate_config(cfg)
    if output.suffix.lower() != ".mp4":
        raise ValueError("output must use the .mp4 extension")
    if output.exists() or output.is_symlink():
        raise FileExistsError("output already exists; choose another filename")
    if not artwork.is_dir():
        raise ValueError("artwork must be an existing directory")
    images = discover_images(artwork)
    if not images:
        raise ValueError("No approved image files found; this tool does not generate artwork")
    if len(images) > 100:
        raise ValueError("at most 100 images are supported per render")
    for image in images:
        validate_image(image)
    output.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    # Each run owns its workspace. Never delete a shared project directory.
    with tempfile.TemporaryDirectory(prefix="mekreflect-reel-") as temp:
        workspace = Path(temp)
        scenes = []
        for index, image in enumerate(images):
            scene = workspace / f"scene_{index + 1:03d}.mp4"
            render_scene(ffmpeg, image, scene, index, cfg)
            scenes.append(scene)
        completed = workspace / "completed.mp4"
        concat_scenes(ffmpeg, scenes, completed)
        # Exclusive creation avoids overwriting an output created during rendering.
        with completed.open("rb") as source, output.open("xb") as target:
            shutil.copyfileobj(source, target)
    return {"scenes": len(images), "estimated_seconds": len(images) * cfg["scene_seconds"], "bytes": output.stat().st_size}


def main() -> int:
    parser = argparse.ArgumentParser(description="Render approved images as a silent MP4")
    parser.add_argument("--artwork", type=Path, default=DEFAULT_ARTWORK)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--scene-seconds", type=float, default=None)
    args = parser.parse_args()

    cfg_doc = json.loads(args.config.read_text(encoding="utf-8"))
    cfg = validate_config(cfg_doc["format"])
    if args.scene_seconds is not None:
        cfg["scene_seconds"] = args.scene_seconds
    output = args.output or (ROOT / "example-output" / "research-reel.mp4")
    try:
        summary = render(args.artwork, cfg, output)
    except (ValueError, FileExistsError) as error:
        parser.error(str(error))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
