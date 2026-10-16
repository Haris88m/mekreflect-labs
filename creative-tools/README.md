# Approved-artwork motion pipeline

I wanted to turn finished page artwork into a short film without asking a model to redraw it. The useful part was giving the production step a clear boundary. The approved images stay the source material. Python checks them, orders the pages and asks FFmpeg to add camera movement and fades.

This is a source-derived part of my creative R&D at [MEKreflect](https://mekreflect.com/), extracted from AI-books. It is a small, executable tool, not a generative video model. The public example uses generated geometric test images, not the original story, family material or illustrations.

## Run it

Python 3.10 or newer and the two dependencies in `requirements.txt` are needed. Tested here with Python 3.12, Pillow 11.3 and imageio-ffmpeg 0.6. A compatible FFmpeg executable is supplied by imageio-ffmpeg on supported platforms. No API key or paid model is used.

```sh
python -m pip install -r requirements.txt
python make_example.py
python render_reel.py
python -m unittest discover -s tests -v
```

The example creates three geometry-only PNG files under `example-output/images` and a silent six-second MP4 at `example-output/research-reel.mp4`. These generated files are ignored by Git. Choose another output filename for a second render. Existing outputs are deliberately never replaced.

To use your own approved images, supply a directory and a JSON config with the same structure as `example.json`.

```sh
python render_reel.py --artwork approved-images --config example.json --output my-reel.mp4
```

Images are naturally sorted, so page-2 precedes page-10. PNG, JPEG and WebP are supported. A render accepts at most 100 images, even dimensions between 16 and 4096, 1 to 60 fps and scenes up to 60 seconds. The reviewed encoding path is H.264 and yuv420p. There is no audio, text generation or model API.

## What the implementation does

```text
Approved images
    → file discovery and image decoding checks
    → validated dimensions, timing and encoding settings
    → separate temporary workspace for this render
    → four alternating camera-motion patterns and fades
    → scene concatenation
    → exclusive creation of the final MP4
```

The image files are not rewritten. The video framing does crop and scale them to the requested aspect ratio. Review the result visually if an edge, caption or important subject must remain visible.

## Verified behavior

Fourteen tests pass, including a real FFmpeg encode/decode of three synthetic scenes. That test checks output dimensions, frame rate, 12 decoded frames, unchanged source images and preservation of an unrelated workspace. Other tests cover invalid settings, missing and corrupt inputs, ordering, refused output replacement and cleanup after an encoder failure.

The original code used a fixed `.tmp_render` directory and removed it before each run. The export uses a unique temporary workspace. It also refuses to overwrite an existing output and rejects invalid numeric settings before starting the encoder. These are new release-hardening changes, not claims about the historical project.

This is not an assessment of film quality, marketing performance, image rights or untrusted-file security. Only use files you have permission to process. Image decoding and FFmpeg are local native dependencies, not a sandbox. If a disk write fails while publishing a completed render, a partial output may remain; choose a new filename after inspecting it. Dependency versions should be reviewed before deployment as a multi-user service.

See [the case study](CASE-STUDY.md) and [source provenance](PROVENANCE.md).
