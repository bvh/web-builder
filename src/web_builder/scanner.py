import logging
import os
from pathlib import Path

from web_builder.node import Node

log = logging.getLogger("web-builder")


def scan_source(source: str) -> Node:
    log.debug("scan_source START")
    result = None
    path = Path(source)
    if path.exists():
        if path.is_dir():
            result = _scan_directory(path)
        else:
            raise ValueError(f"source path ({source}) must be a directory")
    else:
        raise ValueError(f"source path ({source}) does not exist")
    return result


def _scan_directory(path: Path, parent: Node | None = None) -> Node:
    current = Node(path, parent)
    with os.scandir(path) as entries:
        for entry in entries:
            # skip dotfiles and symbolic links
            if not (entry.name.startswith(".") or entry.is_symlink()):
                if entry.is_dir():
                    # Output discarded, since the node has already saved itself
                    # to current's list of children.
                    _scan_directory(Path(entry.path), parent=current)

                # Special case for `index.md` and `config.json`. These are
                # not treated as nodes, but rather as content and configuration
                # for the current node.
                elif entry.name.lower() == "config.json":
                    current.add_config(Path(entry.path))
                elif entry.name.lower() == "index.md":
                    current.add_content(Path(entry.path))

                elif entry.is_file():
                    # Output discarded, since the node has already saved itself
                    # to current's list of children.
                    Node(Path(entry.path), parent=current)

                # This shouldn't happen. We skip symbolic links, and handle
                # both directories and files.
                else:
                    log.warning(f"{entry.path} is an entry of unknown type")

    return current
