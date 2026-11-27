import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageOps

ATLAS_SIZE = (1024, 1536)
PAGE_SIZE = (512, 768)
MAX_FILE_SIZE = 20 * 1024 * 1024
PAGE_NAMES = ("1", "2", "3", "4")
PAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


def select_assets(assets):
    files = {asset["name"].lower(): asset for asset in assets}
    if "atlas.png" in files and len(assets) == 1:
        return [files["atlas.png"]]

    pages = []
    for number in PAGE_NAMES:
        matches = [files[number + suffix] for suffix in PAGE_EXTENSIONS if number + suffix in files]
        if len(matches) != 1:
            break
        pages.append(matches[0])
    if len(pages) == len(assets) == 4:
        return pages
    raise ValueError("Attach atlas.png alone, or four images named 1, 2, 3 and 4 with PNG, JPEG or WebP extensions.")


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


def build_atlas(images, output):
    if len(images) == 1:
        with Image.open(images[0], formats=["PNG"]) as atlas:
            if atlas.size != ATLAS_SIZE:
                raise ValueError("atlas.png must be 1024 by 1536 pixels.")
            atlas.verify()
        with Image.open(images[0], formats=["PNG"]) as atlas:
            atlas.load()
        shutil.copyfile(images[0], output)
        return

    atlas = Image.new("RGB", ATLAS_SIZE, "white")
    for index, path in enumerate(images):
        with Image.open(path, formats=["PNG", "JPEG", "WEBP"]) as image:
            page = ImageOps.fit(
                ImageOps.exif_transpose(image).convert("RGBA"),
                PAGE_SIZE, method=Image.Resampling.LANCZOS,
            )
        atlas.paste(page, ((index % 2) * PAGE_SIZE[0], (index // 2) * PAGE_SIZE[1]), page)
    atlas.save(output, format="PNG", optimize=True)


def main():
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    output_dir = Path("_site")
    output_dir.mkdir()
    with tempfile.TemporaryDirectory() as directory:
        release = event.get("release")
        tag = os.environ.get("MAGAZINE_RELEASE_TAG")
        if tag:
            if not tag.startswith("mag-"):
                raise ValueError("The release tag must start with mag-.")
            repository = os.environ["GITHUB_REPOSITORY"]
            release = json.loads(subprocess.check_output(
                ["gh", "api", f"repos/{repository}/releases/tags/{quote(tag, safe='')}"]
            ))
            if release["draft"]:
                raise ValueError("Publish the release first.")
        if release:
            assets = select_assets(release["assets"])
            images = download_assets(assets, Path(directory))
        else:
            images = [Path("atlas.png")]
        build_atlas(images, output_dir / "atlas.png")


if __name__ == "__main__":
    main()

