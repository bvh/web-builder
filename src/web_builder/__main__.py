import logging
import sys

log = logging.getLogger("web-builder")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)


def main() -> None:
    log.debug("START")
    log.info("Hello, Web Builder!")
    log.debug("END")
    return 0


if __name__ == "__main__":
    sys.exit(main())
