from __future__ import annotations

from pathlib import Path


class ModuleAnalyzer:
    """
    Detects repository modules from a file path.

    Responsibilities
    ----------------
    - Detect the module containing the file
    - Detect the package hierarchy
    - Return structured module information

    Example
    -------
    app/services/indexing_service.py

    Returns

    {
        "module": "services",
        "package": "app.services"
    }
    """

    def analyze(
        self,
        file_path: str,
    ) -> dict:

        path = Path(file_path)

        parts = list(path.parts)

        module = None
        package = ""

        # --------------------------------------------
        # Detect module
        # app/services/indexing_service.py
        #      ↑
        #   services
        # --------------------------------------------

        if "app" in parts:

            index = parts.index("app")

            if index + 1 < len(parts):

                module = parts[index + 1]

                package = ".".join(
                    parts[index:-1]
                )

        else:

            if len(parts) >= 2:

                module = parts[-2]

                package = ".".join(
                    parts[:-1]
                )

        return {

            "module": module,

            "package": package,
        }