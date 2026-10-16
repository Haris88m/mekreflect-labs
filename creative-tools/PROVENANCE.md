# Source provenance and publication boundary

Prepared 16 October 2026.

## Existing implementation

This export derives from the private `Haris88m/AI-books` repository, commit `539d278171ab96b621195e435777d5865d5e45d0`, specifically `scripts/render_reel.py`. The original Git blob is `511cc4acddbce388b1ea58f7847047fae25c0e4a`.

Retained implementation includes natural ordering, Pillow verification, the four FFmpeg zoom/pan patterns, scene encoding and concat demuxer use. It is source-derived code, not a newly invented description of an absent system. The original repository and its history are unchanged.

## Added for this public export

- Generic names and an example configuration independent of the private series.
- Geometry-only example generator. No original artwork was present in the reviewed tracked tree and none was obtained or exported.
- Configuration validation and a bounded local CLI contract.
- Per-run temporary workspace rather than deletion of a shared project folder.
- Exclusive final output creation rather than unrequested replacement.
- POSIX path formatting for the FFmpeg concat list.
- Fourteen regression tests, including real synthetic encode/decode.
- Documentation and this case study.

AI-assisted coding was used. Haris supplied the project direction and operating constraints. The release work was performed with Codex and reviewed by the coordinating agent. Tests are software observations, not proof of authorship, user adoption or creative quality.

## Excluded

Family names, series/story text, private prompts, conversations, original artwork, photos, rendered private media, original Actions files and Git history are excluded. The release has no remote service configuration or account identifiers. Its only public organization link is MEKreflect's website.

## Reproduction and limits

On 16 October 2026, `python -m unittest discover -s tests -v` ran fourteen tests successfully under Python 3.12, Pillow 11.3.0, imageio-ffmpeg 0.6.0 and its FFmpeg 7.1 Windows executable. The synthetic three-scene integration fixture decoded 12 frames at 64×96 and 10 fps. A separate default example render is six seconds at 360×640 and 24 fps.

The private red test ran the original orchestration in an owned temporary directory with intercepted encoder calls. It reproduced deletion of the shared temporary sentinel and replacement of an existing output. No user files were at risk. The new tests verify non-replacement, isolated workspaces and cleanup of the owned temporary directory after encoder failure.

No live model, paid API, network service, original story render or human visual-quality study was run. Installing dependencies can access package servers; normal rendering has no network operation in this source. A no-finding source scan does not establish security certification or full intellectual-property clearance.

## Rights and dependencies

This publication makes the selected source available for inspection. No blanket license is added to the owner's previously unlicensed code. Pillow and imageio-ffmpeg retain their respective third-party licenses. FFmpeg's license depends on the distributed build and enabled codecs; its bundled executable is not copied into this repository. Review upstream licenses before redistribution or commercial bundling.
