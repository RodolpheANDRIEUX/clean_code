"""Public API of the ``structures`` domain package.

Usage::

    from src.domain.structures import LinkedList, Tree, Graph

    # Linked list
    lst: LinkedList[int] = LinkedList()

    # Binary tree
    bt: Tree[int] = Tree(max_children=2)

    # Undirected graph
    g: Graph[str] = Graph()
"""
from .base_structure import BaseStructure
from .exceptions import ChildLimitExceededError, NodeNotFoundError, StructureError
from .graph import Graph
from .linked_list import LinkedList
from .tree import Tree

__all__ = [
    "BaseStructure",
    "LinkedList",
    "Tree",
    "Graph",
    "StructureError",
    "ChildLimitExceededError",
    "NodeNotFoundError",
]
