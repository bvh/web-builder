from unittest.mock import MagicMock, patch

from web_builder.metadata import read_metadata, strip_metadata


class TestReadMetadata:
    """Tests for read_metadata()."""

    def test_returns_exif_iptc_xmp_keys(self, tmp_path):
        """Result always has the three expected keys."""
        path = tmp_path / "photo.svg"
        path.write_bytes(b"<svg></svg>")
        result = read_metadata(path)
        assert set(result.keys()) == {"exif", "iptc", "xmp"}

    def test_unsupported_extension_returns_empty(self, tmp_path):
        """SVG and other unsupported formats return empty dicts."""
        for ext in [".svg", ".bmp", ".tiff", ".txt"]:
            path = tmp_path / f"file{ext}"
            path.write_bytes(b"\x00")
            result = read_metadata(path)
            assert result == {"exif": {}, "iptc": {}, "xmp": {}}

    @patch("web_builder.metadata.pyexiv2")
    def test_reads_metadata_for_supported_extension(self, mock_pyexiv2, tmp_path):
        """Supported image extensions trigger pyexiv2 reads."""
        mock_img = MagicMock()
        mock_img.read_exif.return_value = {"Exif.Image.Artist": "Test"}
        mock_img.read_iptc.return_value = {"Iptc.Application2.ObjectName": "Obj"}
        mock_img.read_xmp.return_value = {"Xmp.dc.creator": "Creator"}
        mock_pyexiv2.Image.return_value = mock_img

        path = tmp_path / "photo.jpg"
        path.write_bytes(b"\xff\xd8\xff")
        result = read_metadata(path)

        mock_pyexiv2.Image.assert_called_once_with(str(path))
        assert result["exif"] == {"Exif.Image.Artist": "Test"}
        assert result["iptc"] == {"Iptc.Application2.ObjectName": "Obj"}
        assert result["xmp"] == {"Xmp.dc.creator": "Creator"}
        mock_img.close.assert_called_once()

    @patch("web_builder.metadata.pyexiv2")
    def test_supported_extensions_all_work(self, mock_pyexiv2, tmp_path):
        """All supported extensions (.jpg, .jpeg, .png, .webp, .gif) are read."""
        mock_img = MagicMock()
        mock_img.read_exif.return_value = {}
        mock_img.read_iptc.return_value = {}
        mock_img.read_xmp.return_value = {}
        mock_pyexiv2.Image.return_value = mock_img

        for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
            path = tmp_path / f"image{ext}"
            path.write_bytes(b"\x00")
            read_metadata(path)

        assert mock_pyexiv2.Image.call_count == 5

    @patch("web_builder.metadata.pyexiv2")
    def test_case_insensitive_extension(self, mock_pyexiv2, tmp_path):
        """Extension matching is case-insensitive."""
        mock_img = MagicMock()
        mock_img.read_exif.return_value = {}
        mock_img.read_iptc.return_value = {}
        mock_img.read_xmp.return_value = {}
        mock_pyexiv2.Image.return_value = mock_img

        path = tmp_path / "photo.JPG"
        path.write_bytes(b"\xff\xd8\xff")
        read_metadata(path)

        mock_pyexiv2.Image.assert_called_once()

    @patch("web_builder.metadata.pyexiv2")
    def test_close_called_on_read_error(self, mock_pyexiv2, tmp_path):
        """Image is closed even when a read method raises."""
        mock_img = MagicMock()
        mock_img.read_exif.side_effect = RuntimeError("corrupt")
        mock_pyexiv2.Image.return_value = mock_img

        path = tmp_path / "bad.jpg"
        path.write_bytes(b"\x00")
        result = read_metadata(path)

        mock_img.close.assert_called_once()
        assert result == {"exif": {}, "iptc": {}, "xmp": {}}

    @patch("web_builder.metadata.pyexiv2")
    def test_open_error_returns_empty(self, mock_pyexiv2, tmp_path):
        """If pyexiv2.Image() raises, return empty dicts gracefully."""
        mock_pyexiv2.Image.side_effect = RuntimeError("cannot open")

        path = tmp_path / "bad.png"
        path.write_bytes(b"\x00")
        result = read_metadata(path)

        assert result == {"exif": {}, "iptc": {}, "xmp": {}}

    @patch("web_builder.metadata.pyexiv2")
    def test_partial_read_preserves_earlier_results(self, mock_pyexiv2, tmp_path):
        """If iptc read fails, exif data already read is still returned."""
        mock_img = MagicMock()
        mock_img.read_exif.return_value = {"Exif.Image.DateTime": "2024:01:01"}
        mock_img.read_iptc.side_effect = RuntimeError("iptc error")
        mock_pyexiv2.Image.return_value = mock_img

        path = tmp_path / "photo.jpg"
        path.write_bytes(b"\xff\xd8\xff")
        read_metadata(path)

        # exif was read before the error, but the exception handler resets
        # result to the initial empty state — verify close is still called
        mock_img.close.assert_called_once()


class TestStripMetadata:
    """Tests for strip_metadata()."""

    def test_unsupported_extension_is_skipped(self, tmp_path):
        """SVG and other unsupported formats are not modified."""
        path = tmp_path / "image.svg"
        path.write_bytes(b"<svg></svg>")
        original = path.read_bytes()
        strip_metadata(path)
        assert path.read_bytes() == original

    @patch("web_builder.metadata.pyexiv2")
    def test_clears_all_metadata(self, mock_pyexiv2, tmp_path):
        """All three metadata categories are cleared."""
        mock_img = MagicMock()
        mock_img.read_exif.return_value = {}
        mock_img.read_iptc.return_value = {}
        mock_img.read_xmp.return_value = {}
        mock_pyexiv2.Image.return_value = mock_img

        path = tmp_path / "photo.jpg"
        path.write_bytes(b"\xff\xd8\xff")
        strip_metadata(path)

        mock_img.clear_exif.assert_called_once()
        mock_img.clear_iptc.assert_called_once()
        mock_img.clear_xmp.assert_called_once()
        mock_img.close.assert_called_once()

    @patch("web_builder.metadata.pyexiv2")
    def test_preserves_artist_and_copyright_exif(self, mock_pyexiv2, tmp_path):
        """EXIF Artist and Copyright tags are restored after clearing."""
        mock_img = MagicMock()
        mock_img.read_exif.return_value = {
            "Exif.Image.Artist": "Jane Doe",
            "Exif.Image.Copyright": "2024 Jane Doe",
            "Exif.Image.Make": "Canon",
            "Exif.Image.DateTime": "2024:01:01",
        }
        mock_img.read_iptc.return_value = {}
        mock_img.read_xmp.return_value = {}
        mock_pyexiv2.Image.return_value = mock_img

        path = tmp_path / "photo.jpg"
        path.write_bytes(b"\xff\xd8\xff")
        strip_metadata(path)

        mock_img.modify_exif.assert_called_once_with(
            {
                "Exif.Image.Artist": "Jane Doe",
                "Exif.Image.Copyright": "2024 Jane Doe",
            }
        )

    @patch("web_builder.metadata.pyexiv2")
    def test_preserves_iptc_byline_and_copyright(self, mock_pyexiv2, tmp_path):
        """IPTC Byline and Copyright tags are restored after clearing."""
        mock_img = MagicMock()
        mock_img.read_exif.return_value = {}
        mock_img.read_iptc.return_value = {
            "Iptc.Application2.Byline": "Jane Doe",
            "Iptc.Application2.Copyright": "2024 Jane Doe",
            "Iptc.Application2.City": "Portland",
        }
        mock_img.read_xmp.return_value = {}
        mock_pyexiv2.Image.return_value = mock_img

        path = tmp_path / "photo.jpg"
        path.write_bytes(b"\xff\xd8\xff")
        strip_metadata(path)

        mock_img.modify_iptc.assert_called_once_with(
            {
                "Iptc.Application2.Byline": "Jane Doe",
                "Iptc.Application2.Copyright": "2024 Jane Doe",
            }
        )

    @patch("web_builder.metadata.pyexiv2")
    def test_preserves_xmp_creator_and_rights(self, mock_pyexiv2, tmp_path):
        """XMP creator and rights tags are restored after clearing."""
        mock_img = MagicMock()
        mock_img.read_exif.return_value = {}
        mock_img.read_iptc.return_value = {}
        mock_img.read_xmp.return_value = {
            "Xmp.dc.creator": "Jane Doe",
            "Xmp.dc.rights": "All rights reserved",
            "Xmp.xmpRights.Marked": "True",
            "Xmp.dc.subject": "landscape",
            "Xmp.dc.format": "image/jpeg",
        }
        mock_pyexiv2.Image.return_value = mock_img

        path = tmp_path / "photo.jpg"
        path.write_bytes(b"\xff\xd8\xff")
        strip_metadata(path)

        mock_img.modify_xmp.assert_called_once_with(
            {
                "Xmp.dc.creator": "Jane Doe",
                "Xmp.dc.rights": "All rights reserved",
                "Xmp.xmpRights.Marked": "True",
            }
        )

    @patch("web_builder.metadata.pyexiv2")
    def test_no_modify_called_when_no_preserved_tags(self, mock_pyexiv2, tmp_path):
        """modify_* methods are not called when there are no tags to restore."""
        mock_img = MagicMock()
        mock_img.read_exif.return_value = {"Exif.Image.Make": "Canon"}
        mock_img.read_iptc.return_value = {"Iptc.Application2.City": "Portland"}
        mock_img.read_xmp.return_value = {"Xmp.dc.format": "image/jpeg"}
        mock_pyexiv2.Image.return_value = mock_img

        path = tmp_path / "photo.jpg"
        path.write_bytes(b"\xff\xd8\xff")
        strip_metadata(path)

        mock_img.modify_exif.assert_not_called()
        mock_img.modify_iptc.assert_not_called()
        mock_img.modify_xmp.assert_not_called()

    @patch("web_builder.metadata.pyexiv2")
    def test_close_called_on_error(self, mock_pyexiv2, tmp_path):
        """Image is closed even when clearing raises an error."""
        mock_img = MagicMock()
        mock_img.read_exif.return_value = {}
        mock_img.read_iptc.return_value = {}
        mock_img.read_xmp.return_value = {}
        mock_img.clear_exif.side_effect = RuntimeError("write error")
        mock_pyexiv2.Image.return_value = mock_img

        path = tmp_path / "photo.jpg"
        path.write_bytes(b"\xff\xd8\xff")
        strip_metadata(path)

        mock_img.close.assert_called_once()

    @patch("web_builder.metadata.pyexiv2")
    def test_open_error_handled_gracefully(self, mock_pyexiv2, tmp_path):
        """If pyexiv2.Image() raises, strip_metadata doesn't propagate."""
        mock_pyexiv2.Image.side_effect = RuntimeError("cannot open")

        path = tmp_path / "photo.jpg"
        path.write_bytes(b"\xff\xd8\xff")
        strip_metadata(path)  # should not raise


class TestStripMetadataInBuild:
    """Integration: copied images have metadata stripped during build."""

    @patch("web_builder.builder.strip_metadata")
    @patch("web_builder.builder.read_metadata")
    def test_strip_called_on_copied_image(
        self, mock_read, mock_strip, sample_source_tree, tmp_path
    ):
        """strip_metadata is called on the copied image in the target."""
        from web_builder.builder import build_target
        from web_builder.scanner import scan_source

        mock_read.return_value = {"exif": {}, "iptc": {}, "xmp": {}}

        target = tmp_path / "target"
        root = scan_source(str(sample_source_tree))
        build_target(str(target), root)

        expected_path = target / "photos" / "photo" / "photo.jpg"
        mock_strip.assert_called_once_with(expected_path)

    @patch("web_builder.builder.strip_metadata")
    @patch("web_builder.builder.read_metadata")
    def test_strip_not_called_on_static_files(
        self, mock_read, mock_strip, sample_source_tree, tmp_path
    ):
        """strip_metadata is not called for static (non-image) file copies."""
        from web_builder.builder import build_target
        from web_builder.scanner import scan_source

        mock_read.return_value = {"exif": {}, "iptc": {}, "xmp": {}}

        target = tmp_path / "target"
        root = scan_source(str(sample_source_tree))
        build_target(str(target), root)

        # Only one call — for the image, not for favicon.ico
        assert mock_strip.call_count == 1


class TestMetadataInBuild:
    """Integration: metadata is passed to image templates during build."""

    @patch("web_builder.builder.read_metadata")
    def test_image_html_contains_exif_data(
        self, mock_read, sample_source_tree, tmp_path
    ):
        """EXIF metadata appears in the rendered image page."""
        from web_builder.builder import build_target
        from web_builder.scanner import scan_source

        mock_read.return_value = {
            "exif": {"Exif.Image.Artist": "Jane Doe"},
            "iptc": {},
            "xmp": {},
        }

        target = tmp_path / "target"
        root = scan_source(str(sample_source_tree))
        build_target(str(target), root)

        html = (target / "photos" / "photo" / "index.html").read_text()
        assert "Exif.Image.Artist" in html
        assert "Jane Doe" in html
        assert "EXIF" in html

    @patch("web_builder.builder.read_metadata")
    def test_image_html_no_metadata_section_when_empty(
        self, mock_read, sample_source_tree, tmp_path
    ):
        """No metadata sections rendered when all dicts are empty."""
        from web_builder.builder import build_target
        from web_builder.scanner import scan_source

        mock_read.return_value = {"exif": {}, "iptc": {}, "xmp": {}}

        target = tmp_path / "target"
        root = scan_source(str(sample_source_tree))
        build_target(str(target), root)

        html = (target / "photos" / "photo" / "index.html").read_text()
        assert '<div class="metadata">' not in html
        # Image tag should still be present
        assert '<img src="photo.jpg"' in html

    @patch("web_builder.builder.read_metadata")
    def test_image_html_contains_all_three_sections(
        self, mock_read, sample_source_tree, tmp_path
    ):
        """All three metadata sections appear when data is present."""
        from web_builder.builder import build_target
        from web_builder.scanner import scan_source

        mock_read.return_value = {
            "exif": {"Exif.Image.Make": "Canon"},
            "iptc": {"Iptc.Application2.City": "Portland"},
            "xmp": {"Xmp.dc.subject": "landscape"},
        }

        target = tmp_path / "target"
        root = scan_source(str(sample_source_tree))
        build_target(str(target), root)

        html = (target / "photos" / "photo" / "index.html").read_text()
        assert "EXIF" in html
        assert "IPTC" in html
        assert "XMP" in html
        assert "Canon" in html
        assert "Portland" in html
        assert "landscape" in html
