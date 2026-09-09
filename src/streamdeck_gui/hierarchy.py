from typing import Optional

class HierarchyElement[T: HierarchyElement, U: HierarchyElement]:
    def __init__(self) -> None:
        self.parent: Optional[T] = None
        self.root: Optional[U] = None

    def attach(self, parent: T, root: U) -> None:
        assert self.root is None
        self.parent = parent
        self.root = root

    def detach(self) -> None:
        self.parent = self.root = None
