import argparse

from .site import Site
from .node import Node


def main() -> None:
    args = _parse_args()
    site = Site(source=args.source, output=args.output)
    print(site)
    print_nodes(site.root)


def print_nodes(node: Node) -> None:
    print(node)
    for child in node.children:
        print_nodes(child)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Web Builder -- a simple static site generator"
    )
    parser.add_argument(
        "source", type=str, help="path containing site configuration and content"
    )
    parser.add_argument(
        "-o", "--output", type=str, default="./public.out", help="path to output directory"
    )
    return parser.parse_args()
