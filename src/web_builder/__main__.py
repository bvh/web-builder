import argparse
import json
import logging
import os
from pathlib import Path
import sys


log = logging.getLogger("web-builder")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)


def main() -> None:
    log.debug("START")

    args = _parse_args()
    log.debug(f"{args.source=}")
    log.debug(f"{args.target=}")

    if _check_source(args.source):
        print(json.dumps(_scan_directory(args.source), indent=4))

    log.debug("END")
    return 0


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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="simple static site generator")
    parser.add_argument("source", help="site source path")
    parser.add_argument("target", help="HTML output directory")
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
