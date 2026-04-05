import logging
import os

from web_builder.node import File

log = logging.getLogger("web-builder")


def build_target(target: str, root: dict[str, any]) -> None:
    for file in root.get("files"):
        if isinstance(file, File):
            if file.copy_target:
                log.debug(
                    f"COPY  {file.source} -> {os.path.join(target, file.copy_target)}"
                )
            if file.page_target:
                log.debug(
                    f"WRITE {file.source} -> {os.path.join(target, file.page_target)}"
                )
        else:
            build_target(target, file)
    return
