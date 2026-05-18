import os

from jinja2 import Environment, PackageLoader
from markdown_it import MarkdownIt

from .node import Node


class Site:
    def __init__(self, source: str, output: str) -> None:
        self.source = source
        self.output = output
        self.md = MarkdownIt()
        self.jinja = Environment(
            loader=PackageLoader("web_builder", "templates/default")
        )
        self.root = Node(source, site=self)

    def __str__(self) -> str:
        return f"Site(source={self.source}, output={self.output})"
