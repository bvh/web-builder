from datetime import datetime as dt
import logging
import os
from pathlib import Path
import shutil

from markdown_it import MarkdownIt

from web_builder.node import Node

log = logging.getLogger("web-builder")


def build_target(target: str, node: Node) -> None:
    md = MarkdownIt("commonmark", {"typographer": True})
    md.enable(["replacements", "smartquotes"])

    # If the target directory already exists, back it up by renaming. We're
    # using the timestamp as a suffix, which should keep the backup unique.
    test = Path(target)
    if test.exists():
        test.rename(f"{target}.{int(dt.now().timestamp())}")

    # Create the target directory and kick off the build.
    os.makedirs(target)
    _build_node(target, node, md)

    return


def _build_node(target: str, node: Node, md: MarkdownIt) -> None:
    log.info(f">>> {node.type}({node.source}) -> {target}")

    # Create directory, if needed. Pretty URLs are the default (and only)
    # option, so pages and images will need their own directories.
    dir_target = node.directory_target
    if dir_target:
        dir_target = os.path.join(target, dir_target)
        log.info(f"  >>> MAKEDIR: {dir_target}")
        os.makedirs(dir_target)

    # Next, copy static files and images.
    copy_target = node.copy_target
    if copy_target:
        copy_target = os.path.join(target, copy_target)
        log.info(f"  >>> COPY:    {node.source} -> {copy_target}")
        shutil.copy2(node.source, copy_target)

    # Finally, build any HTML pages.
    content_target = node.content_target
    if content_target:
        content_target = os.path.join(target, content_target)
        log.info(f"  >>> WRITE:   {node.content_source} -> {content_target}")
        if node.content_source:
            Path(content_target).write_text(md.render(node.content_source.read_text()))
        else:
            Path(content_target).write_text(md.render("No content provided."))

    # Recursively build all child nodes.
    for child in node.children:
        _build_node(target, child, md)

    return
