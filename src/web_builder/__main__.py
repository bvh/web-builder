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

    print(json.dumps(_scan_directory(args.source), indent=4))

    log.debug("END")
    return 0


def _scan_directory(path: str) -> list[dict[str, any]]:
    result = []
    with os.scandir(os.path.abspath(path)) as entries:
        for entry in entries:
            # ignore dotfies and symbolic links
            if not (entry.name.startswith(".") or entry.is_symlink()):
                stat = entry.stat()
                item = {
                    "name": entry.name,
                    "path": entry.path,
                    "ctime": stat.st_ctime,
                    "mtime": stat.st_mtime,
                }
                if entry.is_dir():
                    item["type"] = "DIR"
                    item["files"] = _scan_directory(entry.path)
                elif entry.is_file():
                    path_obj = Path(entry.path)
                    item["stem"] = path_obj.stem
                    item["suffix"] = path_obj.suffix
                    item["owner"] = path_obj.owner()
                    item["type"] = "FILE"
                else:
                    item["type"] = "UNKNOWN"
                    log.warning(f"unhandled dirEntry type for {entry.path}")
                result.append(item)
    return result


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="simple static site generator")
    parser.add_argument("source", help="site source path")
    parser.add_argument("target", help="HTML output directory")
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
