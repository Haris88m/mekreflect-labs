import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import imageio_ffmpeg

from make_example import generate
from render_reel import discover_images, motion_filter, render, validate_config, validate_image


CFG = {"width": 64, "height": 96, "fps": 10, "scene_seconds": 0.4, "fade_seconds": 0.1}


class RenderContract(unittest.TestCase):
    def test_valid_config_is_copied(self):
        self.assertEqual(validate_config(CFG), CFG)
        self.assertIsNot(validate_config(CFG), CFG)

    def test_config_rejects_bad_numeric_boundaries(self):
        for field, value in (("width", 63), ("height", 0), ("fps", True), ("fps", 61),
                             ("scene_seconds", float("nan")), ("scene_seconds", float("inf")),
                             ("scene_seconds", 0), ("scene_seconds", 61),
                             ("fade_seconds", -1), ("fade_seconds", 0.3),
                             ("fade_seconds", "0.1")):
            with self.subTest(field=field, value=value):
                cfg = dict(CFG, **{field: value})
                with self.assertRaises(ValueError):
                    validate_config(cfg)

    def test_rejects_unreviewed_formats(self):
        for field, value in (("video_codec", "unknown"), ("pixel_format", "rgb24"), ("audio", True)):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    validate_config(dict(CFG, **{field: value}))

    def test_natural_order_and_filter(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            for name in ("page-10.png", "page-2.png", "page-1.jpg", "ignore.txt"):
                (folder / name).touch()
            self.assertEqual([path.name for path in discover_images(folder)], ["page-1.jpg", "page-2.png", "page-10.png"])

    def test_invalid_image_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "invalid.png"
            path.write_bytes(b"not an image")
            with self.assertRaises(OSError):
                validate_image(path)

    def test_motion_has_all_four_patterns(self):
        patterns = [motion_filter(index, 10, 0.4, 64, 96, 0.1) for index in range(4)]
        self.assertEqual(len(set(patterns)), 4)
        self.assertEqual(patterns[0], motion_filter(4, 10, 0.4, 64, 96, 0.1))
        for pattern in patterns:
            self.assertIn("d=4:s=64x96:fps=10", pattern)

    def test_existing_output_preserved_without_running_encoder(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            output = folder / "keep.mp4"
            output.write_bytes(b"existing")
            with patch("render_reel.imageio_ffmpeg.get_ffmpeg_exe") as encoder:
                with self.assertRaises(FileExistsError):
                    render(folder, CFG, output)
                encoder.assert_not_called()
            self.assertEqual(output.read_bytes(), b"existing")

    def test_missing_artwork_has_no_output_side_effects(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            output = folder / "new" / "render.mp4"
            with self.assertRaises(ValueError):
                render(folder / "missing", CFG, output)
            self.assertFalse(output.parent.exists())

    def test_empty_artwork_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            with self.assertRaises(ValueError):
                render(folder, CFG, folder / "render.mp4")

    def test_extension_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            with self.assertRaises(ValueError):
                render(folder, CFG, folder / "render.png")

    def test_example_generator_preserves_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            paths = generate(folder)
            original = paths[0].read_bytes()
            with self.assertRaises(FileExistsError):
                generate(folder)
            self.assertEqual(paths[0].read_bytes(), original)

    def test_actual_render_decode_and_isolated_workspace(self):
        with tempfile.TemporaryDirectory(prefix="creative-render-test-") as temp:
            folder = Path(temp)
            images = folder / "images"
            paths = generate(images)
            originals = [path.read_bytes() for path in paths]
            sentinel = folder / ".tmp_render"
            sentinel.mkdir()
            (sentinel / "owned-by-another-run.txt").write_text("keep", encoding="utf-8")
            output = folder / "complete.mp4"
            result = render(images, CFG, output)
            self.assertEqual(result["scenes"], 3)
            self.assertGreater(result["bytes"], 0)
            self.assertEqual(originals, [path.read_bytes() for path in paths])
            self.assertEqual((sentinel / "owned-by-another-run.txt").read_text(), "keep")
            reader = imageio_ffmpeg.read_frames(str(output), pix_fmt="rgb24")
            metadata = next(reader)
            frames = list(reader)
            self.assertEqual(metadata["size"], (64, 96))
            self.assertAlmostEqual(metadata["fps"], 10)
            self.assertEqual(len(frames), 12)
            self.assertTrue(any(any(frame) for frame in frames))

    def test_encoder_failure_cleans_only_owned_workspace(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            generate(folder / "images")
            workspaces = []
            def failure(ffmpeg, image, output, index, cfg):
                workspaces.append(output.parent)
                raise subprocess.CalledProcessError(1, "synthetic encoder failure")
            with patch("render_reel.render_scene", side_effect=failure):
                with self.assertRaises(subprocess.CalledProcessError):
                    render(folder / "images", CFG, folder / "output.mp4")
            self.assertFalse(workspaces[0].exists())
            self.assertFalse((folder / "output.mp4").exists())
            self.assertEqual(len(list((folder / "images").iterdir())), 3)

    def test_cli_rejects_nan_duration(self):
        source = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, str(source / "render_reel.py"), "--scene-seconds", "nan"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("finite number", result.stderr)


if __name__ == "__main__":
    unittest.main()
