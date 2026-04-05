import logging
import os
from pathlib import Path

log = logging.getLogger("web-builder")


class File:
    def __init__(self, entry: os.DirEntry, path: Path, parent: str | None = None):
        self.name = entry.name
        self.source = entry.path
        stat = entry.stat()
        self.ctime = stat.st_ctime
        self.mtime = stat.st_mtime
        self.stem = path.stem
        self.suffix = path.suffix
        self.owner = path.owner
        path_str = (
            os.path.join(parent, entry.name) if parent is not None else entry.name
        )
        self.path = Path(path_str)

    @property
    def copy_target(self):
        return self.path

    @property
    def page_target(self):
        return None


class Image(File):
    @property
    def copy_target(self):
        return Path(os.path.join(self.path.parent, self.path.stem, self.path.name))

    @property
    def page_target(self):
        return Path(os.path.join(self.path.parent, self.path.stem, "index.html"))


class Content(File):
    @property
    def copy_target(self):
        return None

    @property
    def page_target(self):
        return Path(os.path.join(self.path.parent, self.path.stem, "index.html"))
