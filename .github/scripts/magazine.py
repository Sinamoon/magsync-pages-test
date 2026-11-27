import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

ATLAS_SIZE = (1024, 1536)
PAGE_SIZE = (512, 768)
MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_PAGES = 50
PAGES_PER_SHEET = 8
PAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


def select_assets(assets):
    if len(assets) == 1 and assets[0]["name"].lower() == "atlas.png":
        return assets
    if not 1 <= len(assets) <= MAX_PAGES:
        raise ValueError(f"Attach 1 to {MAX_PAGES} numbered images.")

    numbered = {}
    for asset in assets:
        name = Path(asset["name"].lower())
        number = name.stem
        if name.suffix not in PAGE_EXTENSIONS or number not in map(str, range(1, MAX_PAGES + 1)):
            raise ValueError(f"Unexpected file: {asset['name']}. Use names such as 1.png.")
        index = int(number)
        if index in numbered:
            raise ValueError(f"Page {index} has more than one file.")
        numbered[index] = asset
    for index in range(1, len(assets) + 1):
        if index not in numbered:
            raise ValueError(f"Missing image for page {index}.")
    return [numbered[index] for index in range(1, len(assets) + 1)]


def download_assets(assets, destination):
    paths = []
    for asset in assets:
        if asset["state"] != "uploaded" or not 0 < asset["size"] <= MAX_FILE_SIZE:
            raise ValueError("Each image must finish uploading and be 20 MB or smaller.")
        asset_id = int(asset["id"])
        path = destination / str(asset_id)
        with path.open("wb") as output:
            subprocess.run(
                ["gh", "api", f'repos/{os.environ["GITHUB_REPOSITORY"]}/releases/assets/{asset_id}',
                 "--header", "Accept: application/octet-stream"],
                stdout=output, check=True,
            )
        if path.stat().st_size != asset["size"]:
            raise ValueError("The downloaded image size differs from the uploaded size.")
        paths.append(path)
    return paths


def render_sheet(pages, columns, size):
    sheet = Image.new("RGB", size, "white")
    width, height = PAGE_SIZE
    for index, page in enumerate(pages):
        sheet.paste(page, (index % columns * width, index // columns * height), page)
    return sheet


def build_magazine(images, output, legacy_atlas=False):
    if legacy_atlas:
        with Image.open(images[0], formats=["PNG"]) as atlas:
            if atlas.size != ATLAS_SIZE:
                raise ValueError("atlas.png must be 1024 by 1536 pixels.")
            atlas.verify()
        with Image.open(images[0], formats=["PNG"]) as atlas:
            atlas.load()
            pages = [
                atlas.crop((x, y, x + 512, y + 768)).convert("RGBA")
                for y in (0, 768) for x in (0, 512)
            ]
        shutil.copyfile(images[0], output / "atlas.png")
    else:
        pages = []
        for path in images:
            with Image.open(path, formats=["PNG", "JPEG", "WEBP"]) as image:
                pages.append(ImageOps.fit(
                    ImageOps.exif_transpose(image).convert("RGBA"),
                    PAGE_SIZE, method=Image.Resampling.LANCZOS,
                ))
        render_sheet(pages[:4], 2, ATLAS_SIZE).save(output / "atlas.png", optimize=True)

    # The unshown bottom rows carry the page count in the PNG dimensions.
    sheet_size = (PAGE_SIZE[0] * 4, PAGE_SIZE[1] * 2 + len(pages))
    for start in range(0, len(pages), PAGES_PER_SHEET):
        number = start // PAGES_PER_SHEET + 1
        sheet = render_sheet(pages[start:start + PAGES_PER_SHEET], 4, sheet_size)
        sheet.save(output / f"magazine-{number}.png", optimize=True)


def main():
    repository = os.environ["GITHUB_REPOSITORY"]
    release = json.loads(subprocess.check_output(
        ["gh", "api", f"repos/{repository}/releases/tags/SyncMagazine"]
    ))
    if release["draft"]:
        raise ValueError("Publish the SyncMagazine release first.")
    output_dir = Path("_site")
    output_dir.mkdir()
    with tempfile.TemporaryDirectory() as directory:
        assets = select_assets(release["assets"])
        images = download_assets(assets, Path(directory))
        build_magazine(images, output_dir, assets[0]["name"].lower() == "atlas.png")


if __name__ == "__main__":
    main()

