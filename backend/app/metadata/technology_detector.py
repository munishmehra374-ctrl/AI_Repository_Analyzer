from __future__ import annotations

from app.metadata.technology_registry import TECHNOLOGY_REGISTRY


class TechnologyDetector:
    """
    Detects technologies used in a repository
    from structured import information.
    """

    def detect(
        self,
        imports: list[dict],
    ) -> dict:

        detected = {

            "frameworks": set(),

            "databases": set(),

            "vector_databases": set(),

            "llm_frameworks": set(),

            "llm_providers": set(),

            "dependencies": set(),
        }

        for imported in imports:

            module = imported.get("module")

            if not module:
                continue

            module = module.lower()

            detected["dependencies"].add(module)

            technology = TECHNOLOGY_REGISTRY.get(module)

            if technology is None:
                continue

            category = technology["category"]

            name = technology["name"]

            if category == "Web Framework":

                detected["frameworks"].add(name)

            elif category == "Database":

                detected["databases"].add(name)

            elif category == "Graph Database":

                detected["databases"].add(name)

            elif category == "Vector Database":

                detected["vector_databases"].add(name)

            elif category == "LLM Framework":

                detected["llm_frameworks"].add(name)

            elif category == "LLM Provider":

                detected["llm_providers"].add(name)

        return detected