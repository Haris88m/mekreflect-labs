"""Create geometry-only inputs. No family artwork, faces or personal data."""
from pathlib import Path
from PIL import Image, ImageDraw


def generate(folder: Path) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    paths = [folder / f"page-{number}.png" for number in range(1, 4)]
    if any(path.exists() for path in paths):
        raise FileExistsError("Example images already exist; choose an empty folder")
    for index, path in enumerate(paths):
        image = Image.new("RGB", (360, 640), (12, 26, 30))
        draw = ImageDraw.Draw(image)
        draw.ellipse((40 + index * 20, 160, 240 + index * 20, 360), fill=(40, 190, 170))
        draw.rectangle((40, 440, 300, 480 + index * 20), fill=(230, 209, 159))
        with path.open("xb") as output:
            image.save(output, format="PNG")
    return paths


if __name__ == "__main__":
    generate(Path(__file__).resolve().parent / "example-output" / "images")
