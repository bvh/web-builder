from datetime import datetime as dt
import logging
import os
from pathlib import Path
import shutil

from jinja2 import Environment, PackageLoader
from markdown_it import MarkdownIt

from web_builder.metadata import read_metadata, strip_metadata
from web_builder.node import Node, NodeType

TEMPLATE_MAP = {
    NodeType.HOME: "home.html",
    NodeType.DIRECTORY: "directory.html",
    NodeType.PAGE: "page.html",
    NodeType.IMAGE: "image.html",
}

log = logging.getLogger("web-builder")


def build_target(target: str, node: Node) -> None:
    md = MarkdownIt("commonmark", {"typographer": True})
    md.enable(["replacements", "smartquotes"])

    # If the target directory already exists, back it up by renaming. We're
    # using the timestamp as a suffix, which should keep the backup unique.
    test = Path(target)
    if test.exists():
        test.rename(f"{target}.{int(dt.now().timestamp())}")

    # Autoescape is not enabled, which is **probably** not a security risk so
    # long as we're only processing trusted content. If user generated content
    # enters the picture, we will need to revisit.
    jinja = Environment(loader=PackageLoader("web_builder", "templates/default"))

    # Create the target directory and kick off the build.
    os.makedirs(target)
    _build_node(target, node, md, jinja)


def _build_node(target: str, node: Node, md: MarkdownIt, jinja: Environment) -> None:
    log.info(f">>> {node.type}({node.source}) -> {target}")

    # Create directory, if needed. Pretty URLs are the default (and only)
    # option, so pages and images will need their own directories.
    dir_target = node.directory_target
    if dir_target:
        dir_target = Path(target) / dir_target
        log.info(f"  >>> MAKEDIR: {dir_target}")
        os.makedirs(dir_target)

    # Next, copy static files and images.
    copy_target = node.copy_target
    if copy_target:
        copy_target = Path(target) / copy_target
        log.info(f"  >>> COPY:    {node.source} -> {copy_target}")
        shutil.copy2(node.source, copy_target)
        if node.type == NodeType.IMAGE:
            strip_metadata(copy_target)

    # Finally, build any HTML pages.
    content_target = node.content_target
    if content_target:
        content_target = Path(target) / content_target
        log.info(f"  >>> WRITE:   {node.content_source} -> {content_target}")

        template = jinja.get_template(TEMPLATE_MAP[node.type])
        context = {"title": node.source.name}

        if node.type == NodeType.IMAGE:
            context["filename"] = node.source.name
            metadata = read_metadata(node.source)
            context["exif"] = metadata["exif"]
            context["iptc"] = metadata["iptc"]
            context["xmp"] = metadata["xmp"]
        elif node.content_source:
            context["content"] = md.render(node.content_source.read_text())
        else:
            context["content"] = md.render("No content provided.")

        Path(content_target).write_text(template.render(context))

    # Recursively build all child nodes.
    for child in node.children:
        _build_node(target, child, md, jinja)
