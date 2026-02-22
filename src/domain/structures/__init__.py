"""Public API of the ``structures`` domain package.

Usage::

    from src.domain.structures import LinkedList, Queue, HashTable, Tree, Graph

    # Linked list
    lst: LinkedList[int] = LinkedList()

    # Queue (FIFO)
    q: Queue[int] = Queue()

    # Hash table (dictionary)
    ht: HashTable[str, int] = HashTable()

    # Binary tree
    bt: Tree[int] = Tree(max_children=2)

    # Undirected graph
    g: Graph[str] = Graph()
"""
from .base_structure import BaseStructure
from .exceptions import ChildLimitExceededError, NodeNotFoundError, StructureError
from .graph import Graph
from .hash_table import HashTable
from .linked_list import LinkedList
from .queue import Queue
from .tree import Tree

__all__ = [
    "BaseStructure",
    "LinkedList",
    "Queue",
    "HashTable",
    "Tree",
    "Graph",
    "StructureError",
    "ChildLimitExceededError",
    "NodeNotFoundError",
]
