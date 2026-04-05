import logging
import os
from pathlib import Path

log = logging.getLogger("web-builder")


def scan_source(path: str) -> dict[str, any]:
    log.debug("scan_source START")
    result = None
    if _check_source(path):
        result = _scan_directory(path)
    log.debug("scan_source END")
    return result


def _check_source(source: str) -> bool:
    result = False
    path = Path(os.path.abspath(source))
    if path.exists():
        if path.is_dir():
            result = True
        else:
            raise (ValueError, f"source path ({source}) must be a directory")
    else:
        raise (ValueError, f"source path ({source}) does not exist")
    return result


def _scan_directory(source: str, parent: str | None = None) -> dict[str, any]:
    path = os.path.abspath(source)
    path_obj = Path(path)
    log.debug(f"{parent=}")
    new_parent = os.path.join(parent, path_obj.name) if parent else os.path.sep
    log.debug(f"{new_parent=}")
    result = {
        "type": "DIR" if parent else "HOME",
        "name": path_obj.name,
        "source": os.path.abspath(source),
        "path": new_parent,
        "owner": path_obj.owner(),
        "files": [],
    }
    with os.scandir(path) as entries:
        for entry in entries:
            # skip dotfiles and symbolic links
            if not (entry.name.startswith(".") or entry.is_symlink()):
                if entry.is_dir():
                    result["files"].append(
                        _scan_directory(entry.path, parent=new_parent)
                    )
                elif entry.name.lower() == "config.json":
                    result["config"] = _scan_file(entry)
                elif entry.name.lower() == "index.md":
                    result["content"] = _scan_file(entry)
                elif entry.is_file():
                    result["files"].append(_scan_file(entry, parent=new_parent))
    return result


def _scan_file(entry: os.DirEntry, parent: str | None = None) -> dict[str, any]:
    obj = Path(entry.path)
    suffix = obj.suffix
    stat = entry.stat()
    result = {
        "name": entry.name,
        "source": entry.path,
        "path": os.path.join(parent, entry.name) if parent else entry.name,
        "stem": obj.stem,
        "suffix": suffix,
        "owner": obj.owner(),
        "ctime": stat.st_ctime,
        "mtime": stat.st_mtime,
    }
    if suffix.lower() in [".jpg", ".jpeg"]:
        result["type"] = "IMAGE"
    elif suffix.lower() in [".md"]:
        result["type"] = "CONTENT"
    else:
        result["type"] = "FILE"
    return result
