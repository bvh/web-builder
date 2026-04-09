import logging
from pathlib import Path

import pyexiv2

log = logging.getLogger("web-builder")

# SVG files are XML-based and not supported by pyexiv2/exiv2.
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Tags to preserve when stripping metadata from copied images.
PRESERVE_EXIF = {"Exif.Image.Artist", "Exif.Image.Copyright"}
PRESERVE_IPTC = {"Iptc.Application2.Byline", "Iptc.Application2.Copyright"}
PRESERVE_XMP = {
    "Xmp.dc.creator",
    "Xmp.dc.rights",
    "Xmp.xmpRights.Owner",
    "Xmp.xmpRights.UsageTerms",
    "Xmp.xmpRights.WebStatement",
    "Xmp.xmpRights.Marked",
}


def read_metadata(path: Path) -> dict:
    """Read EXIF, IPTC, and XMP metadata from an image file.

    Returns a dict with keys 'exif', 'iptc', and 'xmp', each mapping to a
    dict of tag name/value pairs. Unsupported formats or read errors return
    empty dicts for all three.
    """
    result = {"exif": {}, "iptc": {}, "xmp": {}}

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return result

    try:
        img = pyexiv2.Image(str(path))
        try:
            result["exif"] = img.read_exif()
            result["iptc"] = img.read_iptc()
            result["xmp"] = img.read_xmp()
        finally:
            img.close()
    except Exception:
        log.warning(f"Failed to read metadata from {path}", exc_info=True)

    return result


def strip_metadata(path: Path) -> None:
    """Strip all metadata from an image except artist/creator and copyright.

    Modifies the file in place. Unsupported formats are silently skipped.
    """
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return

    try:
        img = pyexiv2.Image(str(path))
        try:
            # Read the tags we want to keep before clearing.
            exif_keep = {k: v for k, v in img.read_exif().items() if k in PRESERVE_EXIF}
            iptc_keep = {k: v for k, v in img.read_iptc().items() if k in PRESERVE_IPTC}
            xmp_keep = {k: v for k, v in img.read_xmp().items() if k in PRESERVE_XMP}

            # Clear everything, then restore the preserved tags.
            img.clear_exif()
            img.clear_iptc()
            img.clear_xmp()

            if exif_keep:
                img.modify_exif(exif_keep)
            if iptc_keep:
                img.modify_iptc(iptc_keep)
            if xmp_keep:
                img.modify_xmp(xmp_keep)
        finally:
            img.close()
    except Exception:
        log.warning(f"Failed to strip metadata from {path}", exc_info=True)
