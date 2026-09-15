from app.graph.state import GraphState

from app.tools.retrieval_tool import RetrievalTool
from app.tools.graph_tool import GraphTool
from app.tools.repository_tool import RepositoryTool

import inspect


print("\n" + "=" * 80)
print("### LOADED TOOL_EXECUTOR_NODE.PY ###")
print("FILE:", __file__)
print("=" * 80 + "\n")


class ToolExecutorNode:

    def __init__(
        self,
        retrieval_tool: RetrievalTool,
        graph_tool: GraphTool,
        repository_tool: RepositoryTool,
    ):

        self.tools = {
            "retrieval": retrieval_tool,
            "graph": graph_tool,
            "repository": repository_tool,
        }

        # =====================================================
        # INITIALIZATION DEBUG
        # =====================================================

        print("\n" + "=" * 80)
        print(">>> NEW TOOL EXECUTOR CODE IS RUNNING <<<")

        print(
            "ToolExecutor class:",
            self.__class__,
        )

        print(
            "Retrieval tool:",
            retrieval_tool,
        )

        print(
            "Retrieval tool class:",
            retrieval_tool.__class__,
        )

        print(
            "Retrieval tool file:",
            inspect.getfile(
                retrieval_tool.__class__
            ),
        )

        print("=" * 80 + "\n")

    def __call__(
        self,
        state: GraphState,
    ) -> GraphState:

        question = state["question"]

        repository_id = state.get(
            "repository_id"
        )

        requested_tools = state.get(
            "tools",
            [],
        )

        # =====================================================
        # TOOL EXECUTOR
        # =====================================================

        print("\n" + "=" * 80)
        print("TOOL EXECUTOR")
        print("=" * 80)

        print(
            "Question:",
            question,
        )

        print(
            "Repository ID:",
            repository_id,
        )

        print(
            "Requested Tools:",
            requested_tools,
        )

        # =====================================================
        # RESET OLD CONTEXTS
        # =====================================================

        state["retrieval_context"] = None
        state["graph_context"] = None
        state["repository_context"] = None

        # =====================================================
        # RESET NEW CANDIDATES
        # =====================================================

        state["retrieval_candidates"] = []
        state["graph_candidates"] = []
        state["repository_candidates"] = []

        # =====================================================
        # NO TOOLS
        # =====================================================

        if not requested_tools:

            print(
                "Planner selected NO tools."
            )

            print(
                "=" * 80 + "\n"
            )

            return state

        # =====================================================
        # EXECUTE TOOLS
        # =====================================================

        for tool_name in requested_tools:

            print(
                f"\nRunning Tool: {tool_name}"
            )

            executor = self.tools.get(
                tool_name
            )

            if executor is None:

                print(
                    f"Unknown tool: {tool_name}"
                )

                continue

            # =================================================
            # RUNTIME TOOL DEBUG
            # =================================================

            print(
                "\n========== TOOL RUNTIME DEBUG =========="
            )

            print(
                "Tool name:",
                tool_name,
            )

            print(
                "Tool class:",
                executor.__class__,
            )

            print(
                "Tool module:",
                executor.__class__.__module__,
            )

            print(
                "Tool file:",
                inspect.getfile(
                    executor.__class__
                ),
            )

            print(
                "Execute method:",
                getattr(
                    executor,
                    "execute",
                    None,
                ),
            )

            print(
                "Get candidates method:",
                getattr(
                    executor,
                    "get_candidates",
                    None,
                ),
            )

            print(
                "Available methods:",
                [
                    method
                    for method in dir(executor)
                    if not method.startswith("_")
                ],
            )

            print(
                "========================================\n"
            )

            # =================================================
            # GET CANDIDATES
            # =================================================

            if not hasattr(
                executor,
                "get_candidates",
            ):

                print(
                    f"{tool_name} does not support "
                    "candidate retrieval."
                )

                continue

            # -------------------------------------------------
            # Retrieval + Repository need repository_id
            # -------------------------------------------------

            if tool_name in (
                "retrieval",
                "repository",
            ):

                candidates = executor.get_candidates(
                    question,
                    repository_id=repository_id,
                )

            # -------------------------------------------------
            # Graph keeps its existing interface
            # -------------------------------------------------

            else:

                candidates = executor.get_candidates(
                    question,
                    question_type=state.get(
                        "question_type"
                    ),
                    repository_id=repository_id,
                )
            # =================================================
            # RESULT
            # =================================================

            print(
                f"\nCandidates from {tool_name}:"
            )

            print(
                "Candidate count:",
                len(candidates),
            )

            for index, candidate in enumerate(
                candidates,
                start=1,
            ):

                print(
                    f"\nCandidate {index}:"
                )

                print(
                    candidate
                )

            # =================================================
            # STORE CANDIDATES
            # =================================================

            if tool_name == "retrieval":

                state[
                    "retrieval_candidates"
                ] = candidates

            elif tool_name == "graph":

                state[
                    "graph_candidates"
                ] = candidates

            elif tool_name == "repository":

                state[
                    "repository_candidates"
                ] = candidates

        # =====================================================
        # FINAL TOOL CANDIDATES
        # =====================================================

        print("\n" + "=" * 80)
        print("FINAL TOOL CANDIDATES")
        print("=" * 80)

        print(
            "\nRetrieval Candidates:"
        )

        print(
            state[
                "retrieval_candidates"
            ]
        )

        print(
            "\nGraph Candidates:"
        )

        print(
            state[
                "graph_candidates"
            ]
        )

        print(
            "\nRepository Candidates:"
        )

        print(
            state[
                "repository_candidates"
            ]
        )

        print(
            "=" * 80 + "\n"
        )

        return state