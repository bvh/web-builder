import logging
from pathlib import Path

log = logging.getLogger("web-builder")


class Node:
    def __init__(self, source: Path, parent: Node | None = None) -> None:
        self.source = source
        self.parent = parent
        if self.parent:
            parent.add_child(self)
        self.children = []
        self.config_source = None
        self.content_source = None
        return

    def add_child(self, child: Node) -> None:
        child.parent = self
        self.children.append(child)
        return

    def add_content(self, path: Path) -> None:
        self.content_source = path

    def add_config(self, path: Path) -> None:
        self.config_source = path
