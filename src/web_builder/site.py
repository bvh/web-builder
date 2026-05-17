from .node import Node


class Site:
    def __init__(self, source: str) -> None:
        self.source = source
        self.root = Node(source)

    def __str__(self) -> str:
        return f"Site(source={self.source})"
