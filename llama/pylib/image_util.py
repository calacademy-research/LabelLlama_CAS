import base64
import io
import mimetypes
from pathlib import Path

import requests
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = 300_000_000

TOO_DAMN_SMALL = 10_000
TOO_DAMN_BIG = 32_000_000


IMAGE_ERRORS = (
    AttributeError,
    BufferError,
    ConnectionError,
    EOFError,
    FileNotFoundError,
    Image.DecompressionBombError,
    Image.UnidentifiedImageError,
    IndexError,
    OSError,
    RuntimeError,
    SyntaxError,
    TimeoutError,
    TypeError,
    ValueError,
    requests.exceptions.ReadTimeout,
)

IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")


def has_image_suffix(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_SUFFIXES


def images_only(paths: list[Path]) -> list[Path]:
    return [p for p in paths if has_image_suffix(p)]


def image_dir(dir_: Path) -> list[Path]:
    image_paths = [p for p in dir_.glob("*") if has_image_suffix(p)]
    return image_paths


def image_glob(glob_: str) -> list[Path]:
    image_paths = [p for p in Path().glob(glob_) if has_image_suffix(p)]
    return image_paths


def get_images(dir_: Path | None = None, glob_: str | None = None) -> list[Path]:
    image_paths = []
    image_paths += image_dir(dir_) if dir_ else []
    image_paths += image_glob(glob_) if glob_ else []
    image_paths = sorted(set(image_paths))
    return image_paths


def is_url(value: str) -> bool:
    return value.lower().startswith(("http://", "https://"))


def load_image(source: Path | str) -> tuple[str, str]:
    """Return (base64_image, mime_type) for a local path."""
    with Path(source).open("rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    mime_type, _ = mimetypes.guess_type(source)
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = "application/octet-stream"
    return base64_image, mime_type


def downscale(
    source: Path | str,
    max_dim: int = 1200,
    quality: int = 85,
) -> tuple[str, str]:
    """
    Return (base64_image, mime_type) for a downscaled copy of the image.

    If either dimension exceeds max_dim pixels the image is scaled down
    proportionally and re-encoded as JPEG at the given quality; otherwise
    the original bytes are returned unchanged.
    """
    path = Path(source)
    data = path.read_bytes()
    mime_type, _ = mimetypes.guess_type(path)
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = "application/octet-stream"

    with Image.open(io.BytesIO(data)) as img:
        img = ImageOps.exif_transpose(img)
        if max(img.size) <= max_dim:
            return base64.b64encode(data).decode("utf-8"), mime_type
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        if img.mode != "RGB":
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        return base64.b64encode(buf.getvalue()).decode("utf-8"), "image/jpeg"
