import argparse
import logging
import sys

from web_builder.builder import build_target
from web_builder.scanner import scan_source

log = logging.getLogger("web-builder")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)


def main() -> None:
    log.debug("START")

    args = _parse_args()
    log.debug(f"{args.source=}")
    log.debug(f"{args.target=}")

    root = scan_source(args.source)
    build_target(args.target, root)

    log.debug("END")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="simple static site generator")
    parser.add_argument("source", help="site source path")
    parser.add_argument("target", help="HTML output directory")
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
