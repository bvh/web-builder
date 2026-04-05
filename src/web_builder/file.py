import logging
import os
from pathlib import Path

log = logging.getLogger("web-builder")


class File:
    def __init__(self, entry: os.DirEntry, path: Path, parent: str | None = None):
        stat = entry.stat()
        self.name = entry.name
        self.source = entry.path
        self.path = os.path.join(parent, entry.name) if parent else entry.name
        self.stem = path.stem
        self.suffix = path.suffix
        self.owner = path.owner
        self.ctime = stat.st_ctime
        self.mtime = stat.st_mtime

    def __str__(self):
        return f"{self.__class__.__name__}({self.stem}: {self.path})"


class Image(File):
    pass


class Content(File):
    pass
