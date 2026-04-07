import logging
import os

from web_builder.node import Node

log = logging.getLogger("web-builder")


def build_target(target: str, node: Node, source_root: str | None = None) -> None:
    if not source_root:
        source_root = node.source
        log.info(f"*** source_root={str(source_root)}")
    log.info(f">>> {node.source} -> {os.path.join(target, node.target_path)}")
    for child in node.children:
        build_target(target, child, source_root=source_root)
    return
