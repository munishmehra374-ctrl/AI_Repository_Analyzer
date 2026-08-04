from __future__ import annotations


class StatisticsAnalyzer:
    """
    Computes repository statistics from the extracted AST.

    Responsibilities
    ----------------
    - Count classes
    - Count functions
    - Count imports
    """

    def analyze(
        self,
        extracted_data: dict,
    ) -> dict:

        statistics = {

            "total_classes": 0,

            "total_functions": 0,

            "total_imports": 0,
        }

        statistics["total_classes"] = len(
            extracted_data.get("classes", [])
        )

        statistics["total_functions"] = len(
            extracted_data.get("functions", [])
        )

        statistics["total_imports"] = len(
            extracted_data.get("imports", [])
        )

        return statistics