import os

from markdown_it import MarkdownIt


class Markdown:
    def __init__(self, path: os.PathLike, md: MarkdownIt) -> None:
        self.path = path
        self.md = md

    def render(self) -> str:
        with open(self.path, "r") as f:
            return self.md.render(f.read())

    def __str__(self) -> str:
        return f"Markdown(path={self.path})"
