import base64
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from llama.pylib import image_util


class TestImageUtil(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

        self.png = self.tmp / "sample.png"
        buf = io.BytesIO()
        Image.new("RGB", (10, 10), "red").save(buf, format="PNG")
        self.png_bytes = buf.getvalue()
        self.png.write_bytes(self.png_bytes)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_has_image_suffix_01(self) -> None:
        assert image_util.has_image_suffix(Path("a.png"))
        assert image_util.has_image_suffix(Path("a.JPG"))
        assert image_util.has_image_suffix(Path("a.tiff"))
        assert not image_util.has_image_suffix(Path("a.txt"))
        assert not image_util.has_image_suffix(Path("a.webp"))

    def test_images_only_02(self) -> None:
        paths = [Path("a.png"), Path("b.txt"), Path("c.jpg"), Path("d")]

        assert image_util.images_only(paths) == [
            Path("a.png"),
            Path("c.jpg"),
        ]

    def test_image_dir_03(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dir_ = Path(tmp)
            (dir_ / "a.png").write_bytes(b"png")
            (dir_ / "b.JPG").write_bytes(b"jpg")
            (dir_ / "c.txt").write_bytes(b"txt")
            (dir_ / "sub").mkdir()
            (dir_ / "sub" / "d.png").write_bytes(b"png")

            found = image_util.image_dir(dir_)

        # Only top-level image files (subdir and .txt excluded)
        assert sorted(found) == sorted([dir_ / "a.png", dir_ / "b.JPG"])

    def test_get_images_dedupes_and_sorts_04(self) -> None:
        # image_glob is CWD-relative, so run from inside the temp dir
        old_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            self.addCleanup(os.chdir, old_cwd)

            # Both dir and glob are CWD-relative, as the CLI passes them
            (Path("b.png")).write_bytes(b"png")
            (Path("a.jpg")).write_bytes(b"jpg")
            (Path("c.txt")).write_bytes(b"txt")

            # The glob hits the same files as the dir -> no duplicates
            images = image_util.get_images(dir_=Path(), glob_="*")

        assert images == [Path("a.jpg"), Path("b.png")]

    def test_is_url_05(self) -> None:
        assert image_util.is_url("https://example.com/a.png")
        assert image_util.is_url("HTTP://EXAMPLE.COM/a.png")
        assert not image_util.is_url("ftp://example.com/a.png")
        assert not image_util.is_url("/local/path/a.png")

    def test_load_image_local_path_06(self) -> None:
        base64_image, mime_type = image_util.load_image(self.png)

        assert mime_type == "image/png"
        assert base64.b64decode(base64_image) == self.png_bytes

    def test_load_image_local_str_path_07(self) -> None:
        # Handel strings as paths
        base64_image, mime_type = image_util.load_image(str(self.png))

        assert (base64_image, mime_type) == image_util.load_image(self.png)

    def test_load_image_unknown_mime_08(self) -> None:
        bin_file = self.tmp / "sample.bin"
        bin_file.write_bytes(self.png_bytes)

        base64_image, mime_type = image_util.load_image(bin_file)

        assert mime_type == "application/octet-stream"
        assert base64.b64decode(base64_image) == self.png_bytes

    def test_load_image_url_09(self) -> None:
        resp = MagicMock()
        resp.content = self.png_bytes
        resp.headers = {"Content-Type": "image/jpeg; charset=utf-8"}
        with patch("llama.pylib.image_util.requests.get", return_value=resp) as get:
            base64_image, mime_type = image_util.load_image("https://example.com/a.jpg")

        get.assert_called_once_with("https://example.com/a.jpg", timeout=30)
        assert mime_type == "image/jpeg"
        assert base64.b64decode(base64_image) == self.png_bytes

    def test_load_image_url_mime_fallback_10(self) -> None:
        # A non-image Content-Type falls back to guessing from the URL
        resp = MagicMock()
        resp.content = self.png_bytes
        resp.headers = {"Content-Type": "text/html"}
        with patch("llama.pylib.image_util.requests.get", return_value=resp):
            _, mime_type = image_util.load_image("https://example.com/a.png")

        assert mime_type == "image/png"

    def test_downscale_small_image_unchanged_11(self) -> None:
        small = self.tmp / "small.png"
        buf = io.BytesIO()
        Image.new("RGB", (10, 10), "red").save(buf, format="PNG")
        small.write_bytes(buf.getvalue())

        base64_image, mime_type = image_util.downscale(small)

        assert mime_type == "image/png"
        assert base64.b64decode(base64_image) == small.read_bytes()

    def test_downscale_large_image_12(self) -> None:
        big = self.tmp / "big.png"
        Image.new("RGB", (3000, 2000), "blue").save(big, format="PNG")

        base64_image, mime_type = image_util.downscale(big)

        assert mime_type == "image/jpeg"
        img = Image.open(io.BytesIO(base64.b64decode(base64_image)))
        assert img.format == "JPEG"
        assert img.size == (1200, 800)

    def test_downscale_rgba_converted_to_jpeg_13(self) -> None:
        # JPEG has no alpha channel; RGBA input must be converted
        rgba = self.tmp / "rgba.png"
        Image.new("RGBA", (2000, 1000), (255, 0, 0, 128)).save(rgba, format="PNG")

        base64_image, mime_type = image_util.downscale(rgba)

        assert mime_type == "image/jpeg"
        img = Image.open(io.BytesIO(base64.b64decode(base64_image)))
        assert img.mode == "RGB"
        assert img.size == (1200, 600)

    def test_read_sources_14(self) -> None:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                "# comment line\n"
                "\n"
                "/data/a.png\n"
                "https://example.com/b.jpg\n"
                "   \n"
                "/data/a.png\n"
                "/data/c.txt\n"
            )
            path = Path(f.name)
        self.addCleanup(path.unlink, missing_ok=True)

        sources = image_util.read_sources(path)

        # Duplicates removed, comments/blank lines dropped, URLs stay str
        assert sources == [
            Path("/data/a.png"),
            "https://example.com/b.jpg",
            Path("/data/c.txt"),
        ]


if __name__ == "__main__":
    unittest.main()
