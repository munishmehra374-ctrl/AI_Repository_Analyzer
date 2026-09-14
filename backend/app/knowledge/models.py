from __future__ import annotations

from dataclasses import dataclass, field


# ==========================================================
# Repository Structure
# ==========================================================

@dataclass
class RepositoryNode:
    name: str
    path: str


@dataclass
class FolderNode:
    name: str
    path: str


@dataclass
class FileNode:
    name: str
    path: str
    language: str


# ==========================================================
# Imports
# ==========================================================

@dataclass
class ImportNode:
    statement: str
    module: str | None = None
    alias: str | None = None
    file_path: str | None = None


# ==========================================================
# Classes
# ==========================================================

@dataclass
class ClassNode:
    qualified_name: str
    name: str
    file_path: str
    visibility: str
    base_classes: list[str]
    decorators: list[str]
    start_line: int
    end_line: int
    code: str


# ==========================================================
# Functions
# ==========================================================

@dataclass
class FunctionNode:

    qualified_name: str
    name: str
    file_path: str
    class_name: str | None

    # -----------------------------
    # Function Properties
    # -----------------------------

    is_method: bool
    is_async: bool
    visibility: str
    is_static: bool
    is_classmethod: bool

    # -----------------------------
    # Signature
    # -----------------------------

    parameters: list[dict]
    returns: str | None

    # -----------------------------
    # Behavior
    # -----------------------------

    calls: list[str]
    dependencies: list[dict]
    decorators: list[str]

    # -----------------------------
    # Location
    # -----------------------------

    start_line: int
    end_line: int

    # -----------------------------
    # Source
    # -----------------------------

    code: str


# ==========================================================
# FastAPI Routes
# ==========================================================

@dataclass
class RouteNode:

    method: str
    path: str
    handler: str


# ==========================================================
# Database Models
# ==========================================================

@dataclass
class ModelNode:

    name: str
    file_path: str


# ==========================================================
# Relationships
# ==========================================================

@dataclass
class Relationship:

    source: str
    target: str
    relationship_type: str


# ==========================================================
# Repository Graph
# ==========================================================

@dataclass
class RepositoryGraph:

    repository: RepositoryNode | None = None

    folders: dict[str, FolderNode] = field(
        default_factory=dict
    )

    files: dict[str, FileNode] = field(
        default_factory=dict
    )

    imports: dict[str, ImportNode] = field(
        default_factory=dict
    )

    classes: dict[str, ClassNode] = field(
        default_factory=dict
    )

    functions: dict[str, FunctionNode] = field(
        default_factory=dict
    )

    routes: dict[str, RouteNode] = field(
        default_factory=dict
    )

    models: dict[str, ModelNode] = field(
        default_factory=dict
    )

    relationships: list[Relationship] = field(
        default_factory=list
    )