import os
from pathlib import Path


class Node:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.content = None
        self.children = []
        if self.path.is_dir():
            with os.scandir(self.path) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name == "index.md":
                        self.content = entry.path
                    elif entry.is_file() and entry.name.endswith(".md"):
                        self.children.append(Node(entry.path))
                    elif entry.is_dir():
                        self.children.append(Node(entry.path))

    def __str__(self) -> str:
        return f"Node(path={self.path}, content={self.content}, children={len(self.children)})"
