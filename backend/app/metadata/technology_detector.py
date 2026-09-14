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

            technology = TECHNOLOGY_REGISTRY.get(
                         module
             )

            if technology is None:

                root_module = module.split(".")[0]

                technology = TECHNOLOGY_REGISTRY.get(
                    root_module
                )

            if technology is None:
                continue

            tech_entries = (
                technology
                if isinstance(technology, list)
                else [technology]
            )

            for tech in tech_entries:

                category = tech.get("category")

                name = tech.get("name")

                if category == "Web Framework":

                    detected["frameworks"].add(name)

                elif category in ("Database", "Graph Database"):

                    detected["databases"].add(name)

                elif category == "Vector Database":

                    detected["vector_databases"].add(name)

                elif category == "LLM Framework":

                    detected["llm_frameworks"].add(name)

                elif category == "LLM Provider":

                    detected["llm_providers"].add(name)

        return detected