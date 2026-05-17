import os
from pathlib import Path


from .markdown import Markdown


class Node:
    def __init__(self, path: str, parent: Node = None, site=None) -> None:
        self.path = Path(path)
        self.name = self.path.stem
        self.parent = parent
        self.site = site if site else parent.site if parent else None
        self.markdown = None
        self.config = None
        self.children = []
        self.files = []

        if self.path.is_file() and self.path.name.endswith(".md"):
            # If the node path is a markdown file, then that markdown file
            # is the node's content. Nothing else to do.
            self.markdown = Markdown(self.path, self.site.md)

        elif self.path.is_dir():
            # If the node is a directory, then we need to look for content,
            # config, and child nodes within that directory.
            with os.scandir(self.path) as entries:
                for entry in entries:
                    # skip sybolic links and dotfiles
                    if not (entry.name.startswith(".") or entry.is_symlink()):
                        if entry.is_dir():
                            # This will recursively scan the child directory.
                            # For now, empty directories will be added as nodes,
                            # and we'll allow the build step to decide whether
                            # to include it in the final site or not.
                            self.children.append(Node(entry.path, parent=self))
                        # We've already ruled out symlinks, and above clause
                        # covers directories, so we can assume everything else
                        # is a regular file.
                        elif entry.name == "config.json":
                            # local configuration for this node
                            self.config = Path(entry.path)
                        elif entry.name == "index.md":
                            # markdown content for this node
                            self.markdown = Markdown(Path(entry.path), self.site.md)
                        elif entry.name.endswith(".md"):
                            # child pages within this node
                            self.children.append(Node(entry.path, parent=self))
                        else:
                            # a static file that will need to be copied
                            self.files.append(Path(entry.path))

        else:
            raise ValueError(f"ERROR: {self.path} is not a markdown file or directory")

    def render(self) -> str:
        template = self.site.jinja.get_template("page.html")
        if self.markdown:
            return template.render(content=self.markdown.render())
        else:
            return template.render(content="")

    def __str__(self) -> str:
        lines = [f"== {self.path} =="]
        lines.append(
            f"Node(name={self.name}, markdown={self.markdown}, config={self.config})"
        )
        lines.append(
            f"{self.site.jinja.get_template('page.html').render(content=self.markdown.render() if self.markdown else '')}"
        )
        lines.append("")
        return "\n".join(lines)
