"""Helpers for loading and working with the document catalog configuration."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

import json
import os

from fastapi import HTTPException

DOCUMENT_CONFIG_ENV = "DOCUMENT_CONFIG_PATH"
DEFAULT_CATALOG_PATH = Path("config/document_definitions.json")


@dataclass(frozen=True)
class DocumentDefinition:
    """Typed representation of a single document definition."""

    id: str
    name: str
    prompt_key: Optional[str]
    agent_class: str
    dependencies: List[str]
    category: Optional[str]
    description: Optional[str]
    priority: Optional[str]
    owner: Optional[str]
    status: Optional[str]
    audience: Optional[str]
    stage_label: Optional[str]
    stage_notes: Optional[str]
    must_have: Optional[str]
    usage_frequency: Optional[str]
    notes: Optional[str]
    special_key: Optional[str] = None


def _catalog_path() -> Path:
    env_path = os.getenv(DOCUMENT_CONFIG_ENV)
    if env_path:
        return Path(env_path)
    return DEFAULT_CATALOG_PATH


@lru_cache(maxsize=1)
def load_document_definitions() -> Dict[str, DocumentDefinition]:
    """Load and cache document definitions keyed by ID."""
    catalog_file = _catalog_path()
    if not catalog_file.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Document catalog not found at {catalog_file}",
        )

    payload = json.loads(catalog_file.read_text(encoding="utf-8"))
    documents = payload.get("documents", [])
    definitions: Dict[str, DocumentDefinition] = {}

    for raw in documents:
        doc_id = raw.get("id")
        if not doc_id:
            continue

        stage = raw.get("stage") or {}

        definitions[doc_id] = DocumentDefinition(
            id=doc_id,
            name=raw.get("name", doc_id.title()),
            prompt_key=raw.get("prompt_key"),
            agent_class=raw.get("agent_class", "generic"),
            dependencies=list({dep for dep in raw.get("dependencies", []) if dep}),
            category=raw.get("category"),
            description=raw.get("description"),
            priority=raw.get("priority"),
            owner=raw.get("owner"),
            status=raw.get("status"),
            audience=raw.get("audience"),
            stage_label=stage.get("label"),
            stage_notes=stage.get("notes"),
            must_have=raw.get("must_have"),
            usage_frequency=raw.get("usage_frequency"),
            notes=raw.get("notes"),
            special_key=raw.get("special_key"),
        )

    return definitions


def get_document_by_id(document_id: str) -> Optional[DocumentDefinition]:
    """Return a single document definition, if present."""
    return load_document_definitions().get(document_id)


def reload_catalog() -> None:
    """Clear the cached definitions (useful for tests or when the file changes)."""
    load_document_definitions.cache_clear()  # type: ignore[attr-defined]


def resolve_dependencies(selected_ids: Iterable[str]) -> List[str]:
    """Resolve dependencies for the given document IDs with topological ordering."""
    definitions = load_document_definitions()
    order: List[str] = []
    visiting: Set[str] = set()
    visited: Set[str] = set()

    def visit(doc_id: str) -> None:
        if doc_id in visited:
            return
        if doc_id in visiting:
            raise ValueError(f"Dependency cycle detected involving '{doc_id}'")
        definition = definitions.get(doc_id)
        if not definition:
            raise ValueError(f"Unknown document id '{doc_id}'")

        visiting.add(doc_id)
        for dep_id in definition.dependencies:
            visit(dep_id)
        visiting.remove(doc_id)
        visited.add(doc_id)
        order.append(doc_id)

    for doc_id in dict.fromkeys(selected_ids):
        visit(doc_id)

    return order


def list_document_ids() -> List[str]:
    """Return all document IDs in the catalog."""
    return list(load_document_definitions().keys())


