import os
from pathlib import Path


from .markdown import Markdown


class Node:
    def __init__(self, path: str, parent: Node = None, site=None) -> None:
        self.path = Path(path)
        self.parent = parent
        self.site = site if site else parent.site if parent else None
        self.name = self.path.stem.title()

        self.markdown = None
        self.config = None
        self.children = []
        self.files = []

        if self.parent:
            # If this node has a parent, then join the stem of this node's path
            # to the parent's target directory to get this node's target directory.
            self.target_dir = self.parent.target_dir.joinpath(self.path.stem)
        else:
            # If this node is the root node, then its target directory is just
            # the site's output directory.
            self.target_dir = self.site.output
        # The target file is ALWAYS the target path joins with index.html.
        self.target_file = self.target_dir.joinpath("index.html")

        if self.path.is_file() and self.path.name.endswith(".md"):
            # If the node path is a markdown file, then that markdown file
            # is the node's content. Nothing else to do.
            self.source_dir = self.path.parent
            self.source_file = self.path
            self.markdown = Markdown(self.path, self.site.md)

        elif self.path.is_dir():
            # If the node is a directory, then we need to look for content,
            # config, and child nodes within that directory.

            with os.scandir(self.path) as entries:
                self.source_dir = self.path
                self.source_file = None
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
                            self.source_file = Path(entry.path)
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
            return template.render(title=self.name, content=self.markdown.render())
        else:
            return template.render(title=self.name, content="")

    def __str__(self) -> str:
        lines = [f"== {self.path} =="]
        lines.append(
            f"Node(name={self.name}, markdown={self.markdown}, config={self.config})"
        )
        # lines.append(
        #     f"{self.site.jinja.get_template('page.html').render(content=self.markdown.render() if self.markdown else '')}"
        # )
        lines.append("")
        return "\n".join(lines)
