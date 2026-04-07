from enum import StrEnum
import logging
import os
from pathlib import Path

log = logging.getLogger("web-builder")


class NodeType(StrEnum):
    HOME = "HOME"
    DIRECTORY = "DIRECTORY"
    PAGE = "PAGE"
    IMAGE = "IMAGE"
    STATIC = "STATIC"


class Node:
    def __init__(self, source: Path, parent: Node | None = None) -> None:
        self.source = source
        self.parent = parent
        self.target_path = ""
        if self.parent:
            parent.add_child(self)
            self.target_path = Path(os.path.join(parent.target_path, self.source.name))
        self.type = self._get_type()
        self.children = []
        self.config_source = None
        if self.type == NodeType.PAGE:
            self.content_source = self.source
        else:
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

    def _get_type(self) -> NodeType:
        if self.source.is_dir():
            if self.parent is None:
                type = NodeType.HOME
            else:
                type = NodeType.DIRECTORY
        else:
            if self.source.suffix in [".md"]:
                type = NodeType.PAGE
            elif self.source.suffix in [".jpg", ".jpeg"]:
                type = NodeType.IMAGE
            else:
                type = NodeType.STATIC
        return type

    @property
    def directory_target(self) -> Path | None:
        if self.type in [NodeType.DIRECTORY]:
            path = self.target_path
        elif self.type in [NodeType.IMAGE, NodeType.PAGE]:
            # always use pretty URLs
            path = self.target_path.with_name(self.source.stem)
        else:
            path = None
        return path

    @property
    def copy_target(self) -> Path | None:
        if self.type in [NodeType.IMAGE]:
            path = Path(os.path.join(self.directory_target, self.source.name))
        elif self.type in [NodeType.STATIC]:
            path = self.target_path
        else:
            path = None
        return path

    @property
    def content_target(self) -> Path | None:
        if self.type in [NodeType.DIRECTORY, NodeType.IMAGE, NodeType.PAGE]:
            path = Path(os.path.join(self.directory_target, "index.html"))
        elif self.type in [NodeType.HOME]:
            path = Path("index.html")
        else:
            path = None
        return path
