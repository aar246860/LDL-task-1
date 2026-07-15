from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageStat, UnidentifiedImageError


def image_issue(path: Path, *, minimum_width: int, minimum_height: int) -> str | None:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            grayscale = image.convert("L")
            width, height = grayscale.size
            extrema = grayscale.getextrema()
            standard_deviation = ImageStat.Stat(grayscale).stddev[0]
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        return f"cannot read image: {exc}"
    if extrema is None:
        return "image has no readable luminance extrema"
    low, high = extrema
    if not isinstance(low, (int, float)) or not isinstance(high, (int, float)):
        return "image has non-scalar luminance extrema"
    if width < minimum_width or height < minimum_height:
        return f"image is {width}x{height}; expected at least {minimum_width}x{minimum_height}"
    if high - low < 8 or standard_deviation < 2.0:
        return "image appears blank or nearly uniform"
    return None


def image_fingerprint(path: Path) -> str | None:
    try:
        with Image.open(path) as image:
            pixels = image.convert("RGB").tobytes()
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError):
        return None
    return sha256(pixels).hexdigest()
