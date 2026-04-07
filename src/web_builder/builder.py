import logging
import os

from web_builder.node import Node

log = logging.getLogger("web-builder")


def build_target(target: str, node: Node) -> None:
    log.info(f">>> {node.type}({node.source}) -> {target}")
    dir_target = node.directory_target
    if dir_target:
        log.info(f"  >>> MAKEDIR: {os.path.join(target, dir_target)}")
    copy_target = node.copy_target
    if copy_target:
        log.info(f"  >>> COPY:    {node.source} -> {os.path.join(target, copy_target)}")
    content_target = node.content_target
    if content_target:
        log.info(
            f"  >>> WRITE:   {node.content_source} -> {os.path.join(target, content_target)}"
        )
    for child in node.children:
        build_target(target, child)
    return
