import argparse
from web_builder.site import Site


def main() -> None:
    args = _parse_args()
    site = Site(source=args.source)
    print(site)
    print(site.root.render())


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Web Builder -- a simple static site generator"
    )
    parser.add_argument(
        "source", type=str, help="path containing site configuration and content"
    )
    return parser.parse_args()
