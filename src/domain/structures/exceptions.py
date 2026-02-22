"""Domain exceptions for the structures package."""
from __future__ import annotations


class StructureError(Exception):
    """Base for all structure-related errors."""


class ChildLimitExceededError(StructureError):
    """Raised when inserting a child would exceed a Tree's ``max_children``."""


class NodeNotFoundError(StructureError):
    """Raised when a referenced node does not exist."""
