import argparse
import os
import shutil

from .site import Site
from .node import Node


def main() -> None:
    args = _parse_args()
    site = Site(source=args.source, output=args.output)
    os.makedirs(site.output, exist_ok=True)
    build_nodes(site.root)


def print_nodes(node: Node) -> None:
    print(node)
    for child in node.children:
        print_nodes(child)


def build_nodes(node: Node) -> None:
    print(f"Building node: {node.name} / {node.path} -> {node.target_file}")
    os.makedirs(node.target_dir, exist_ok=True)
    for file in node.files:
        print(f"Copying file: {file} -> {node.target_dir.joinpath(file.name)}")
        shutil.copy(file, node.target_dir.joinpath(file.name))
    with open(f"{node.target_file}", "w") as f:
        f.write(node.render())
    for child in node.children:
        build_nodes(child)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Web Builder -- a simple static site generator"
    )
    parser.add_argument(
        "source", type=str, help="path containing site configuration and content"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./public.out",
        help="path to output directory",
    )
    return parser.parse_args()
