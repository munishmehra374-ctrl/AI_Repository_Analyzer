from __future__ import annotations

import json
from neo4j import GraphDatabase

from app.core.config import settings


def serialize_for_neo4j(val):
    """
    Ensures properties sent to Neo4j are valid primitive types,
    lists of primitive types, or JSON-stringified objects/dicts.
    """
    if val is None or isinstance(val, (str, int, float, bool)):
        return val
    # Neo4j allows lists, but ONLY if every item is a primitive type (str, int, float, bool)
    if isinstance(val, list) and all(isinstance(x, (str, int, float, bool)) for x in val):
        return val
    # Convert dictionaries, object instances, or lists of dicts/objects to JSON strings
    return json.dumps(val, default=str)


class Neo4jStore:
    """
    Stores the Repository Knowledge Graph in Neo4j.
    """

    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(
                settings.NEO4J_USERNAME,
                settings.NEO4J_PASSWORD,
            ),
        )

    def close(self):
        self.driver.close()

    # =====================================================
    # Clear Repository Graph
    # =====================================================

    def clear_repository(
        self,
        repository_id: str,
    ):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (n)
                WHERE n.repository_id = $repository_id
                DETACH DELETE n
                """,
                repository_id=repository_id,
            )

        print(
            "Cleared Neo4j graph for repository:",
            repository_id,
        )

    # =====================================================
    # Public API
    # =====================================================

    def store_graph(
        self,
        graph,
        repository_id: str,
    ):
        # -------------------------------------------------
        # Remove ONLY this repository's previous graph.
        # Other repositories remain untouched.
        # -------------------------------------------------

        self.clear_repository(repository_id)

        with self.driver.session() as session:
            self._store_repository(
                session,
                graph,
                repository_id,
            )

            self._store_folders(
                session,
                graph,
                repository_id,
            )

            self._store_files(
                session,
                graph,
                repository_id,
            )

            self._store_imports(
                session,
                graph,
                repository_id,
            )

            self._store_classes(
                session,
                graph,
                repository_id,
            )

            self._store_functions(
                session,
                graph,
                repository_id,
            )

            self._store_routes(
                session,
                graph,
                repository_id,
            )

            self._store_models(
                session,
                graph,
                repository_id,
            )

            self._store_relationships(
                session,
                graph,
                repository_id,
            )

    # =====================================================
    # Incremental Graph Update
    # =====================================================

    def update_graph(
        self,
        graph,
        repository_id: str,
        changed_files: list[str],
    ):
        if not changed_files:
            print("No changed files. Neo4j graph unchanged.")
            return

        changed_files = {str(file_path) for file_path in changed_files}

        print("\n========== NEO4J INCREMENTAL GRAPH UPDATE ==========")
        print("Repository:", repository_id)
        print("Changed files:", len(changed_files))

        for file_path in changed_files:
            print("  ", file_path)

        print("=====================================================\n")

        # -------------------------------------------------
        # Identify entities belonging to changed files
        # -------------------------------------------------

        changed_classes = {
            cls.qualified_name
            for cls in graph.classes.values()
            if str(cls.file_path) in changed_files
        }

        changed_class_names = {
            cls.name
            for cls in graph.classes.values()
            if str(cls.file_path) in changed_files
        }

        changed_functions = {
            function.qualified_name
            for function in graph.functions.values()
            if str(function.file_path) in changed_files
        }

        changed_imports = {
            imp.statement
            for imp in graph.imports.values()
            if imp.file_path and str(imp.file_path) in changed_files
        }

        changed_models = {
            model.name
            for model in graph.models.values()
            if str(model.file_path) in changed_files
        }

        changed_routes = {
            route.path
            for route in graph.routes.values()
            if getattr(route, "file_path", None)
            and str(route.file_path) in changed_files
        }

        # -------------------------------------------------
        # Delete ONLY nodes belonging to changed files
        # This also removes their old relationships.
        # -------------------------------------------------

        print("\nDELETING CHANGED FILE DATA:")
        for file_path in changed_files:
            print("  DELETE:", file_path)

        with self.driver.session() as session:
            session.run(
                """
                MATCH (n)
                WHERE
                    n.repository_id = $repository_id
                    AND (
                        n.file_path IN $changed_files
                        OR n.path IN $changed_files
                    )
                DETACH DELETE n
                """,
                repository_id=repository_id,
                changed_files=list(changed_files),
            )

            # -------------------------------------------------
            # Store ONLY changed files
            # -------------------------------------------------

            for file in graph.files.values():
                if str(file.path) not in changed_files:
                    continue

                session.run(
                    """
                    MERGE (
                        f:File {
                            path:$path,
                            repository_id:$repository_id
                        }
                    )
                    SET
                        f.name=$name,
                        f.language=$language
                    """,
                    path=file.path,
                    name=file.name,
                    language=file.language,
                    repository_id=repository_id,
                )

            # -------------------------------------------------
            # Store ONLY changed imports
            # -------------------------------------------------

            for imp in graph.imports.values():
                if not imp.file_path or str(imp.file_path) not in changed_files:
                    continue

                session.run(
                    """
                    MERGE (
                        i:Import {
                            statement:$statement,
                            repository_id:$repository_id
                        }
                    )
                    SET
                        i.module=$module,
                        i.alias=$alias,
                        i.file_path=$file_path
                    """,
                    statement=imp.statement,
                    module=getattr(imp, "module", None),
                    alias=getattr(imp, "alias", None),
                    file_path=imp.file_path,
                    repository_id=repository_id,
                )

            # -------------------------------------------------
            # Store ONLY changed classes
            # -------------------------------------------------

            for cls in graph.classes.values():
                if str(cls.file_path) not in changed_files:
                    continue

                session.run(
                    """
                    MERGE (
                        c:Class {
                            name:$name,
                            repository_id:$repository_id
                        }
                    )
                    SET
                        c.qualified_name=$qualified_name,
                        c.file_path=$file_path,
                        c.visibility=$visibility,
                        c.base_classes=$base_classes,
                        c.decorators=$decorators,
                        c.start_line=$start_line,
                        c.end_line=$end_line,
                        c.code=$code
                    """,
                    name=cls.name,
                    qualified_name=getattr(cls, "qualified_name", cls.name),
                    file_path=cls.file_path,
                    visibility=getattr(cls, "visibility", "public"),
                    base_classes=serialize_for_neo4j(getattr(cls, "base_classes", [])),
                    decorators=serialize_for_neo4j(getattr(cls, "decorators", [])),
                    start_line=cls.start_line,
                    end_line=cls.end_line,
                    code=getattr(cls, "code", ""),
                    repository_id=repository_id,
                )

            # -------------------------------------------------
            # Store ONLY changed functions
            # -------------------------------------------------

            for function in graph.functions.values():
                if str(function.file_path) not in changed_files:
                    continue

                session.run(
                    """
                    MERGE (
                        f:Function {
                            qualified_name:$qualified_name,
                            repository_id:$repository_id
                        }
                    )
                    SET
                        f.name=$name,
                        f.file_path=$file_path,
                        f.class_name=$class_name,
                        f.is_method=$is_method,
                        f.is_async=$is_async,
                        f.visibility=$visibility,
                        f.is_static=$is_static,
                        f.is_classmethod=$is_classmethod,
                        f.parameters=$function_parameters,
                        f.returns=$returns,
                        f.calls=$calls,
                        f.dependencies=$dependencies,
                        f.decorators=$decorators,
                        f.start_line=$start_line,
                        f.end_line=$end_line,
                        f.code=$code
                    """,
                    qualified_name=function.qualified_name,
                    name=function.name,
                    file_path=function.file_path,
                    class_name=function.class_name,
                    is_method=function.is_method,
                    is_async=function.is_async,
                    visibility=function.visibility,
                    is_static=function.is_static,
                    is_classmethod=function.is_classmethod,
                    function_parameters=serialize_for_neo4j(function.parameters),
                    returns=serialize_for_neo4j(function.returns),
                    calls=serialize_for_neo4j(function.calls),
                    dependencies=serialize_for_neo4j(function.dependencies),
                    decorators=serialize_for_neo4j(function.decorators),
                    start_line=function.start_line,
                    end_line=function.end_line,
                    code=function.code,
                    repository_id=repository_id,
                )

            # -------------------------------------------------
            # Store ONLY changed routes
            # -------------------------------------------------

            for route in graph.routes.values():
                route_file_path = getattr(route, "file_path", None)

                if (
                    not route_file_path
                    or str(route_file_path) not in changed_files
                ):
                    continue

                session.run(
                    """
                    MERGE (
                        r:Route {
                            path:$path,
                            method:$method,
                            repository_id:$repository_id
                        }
                    )
                    SET
                        r.handler=$handler,
                        r.file_path=$file_path
                    """,
                    path=route.path,
                    method=route.method,
                    handler=route.handler,
                    file_path=route_file_path,
                    repository_id=repository_id,
                )

            # -------------------------------------------------
            # Store ONLY changed models
            # -------------------------------------------------

            for model in graph.models.values():
                if str(model.file_path) not in changed_files:
                    continue

                session.run(
                    """
                    MERGE (
                        m:Model {
                            name:$name,
                            repository_id:$repository_id
                        }
                    )
                    SET
                        m.file_path=$file_path
                    """,
                    name=model.name,
                    file_path=model.file_path,
                    repository_id=repository_id,
                )

            # =================================================
            # Relationships
            # =================================================

            changed_entities = (
                changed_files
                | changed_classes
                | changed_class_names
                | changed_functions
                | changed_imports
                | changed_models
                | changed_routes
            )

            for relationship in graph.relationships:
                relationship_type = relationship.relationship_type
                source = str(relationship.source)
                target = str(relationship.target)

                if (
                    source not in changed_entities
                    and target not in changed_entities
                ):
                    continue

                query = {
                    "HAS_FILE": """
                    MATCH (
                        a:Folder {
                            path:$source,
                            repository_id:$repository_id
                        }
                    )
                    MATCH (
                        b:File {
                            path:$target,
                            repository_id:$repository_id
                        }
                    )
                    MERGE (a)-[:HAS_FILE]->(b)
                    """,
                    "HAS_CLASS": """
                    MATCH (
                        a:File {
                            path:$source,
                            repository_id:$repository_id
                        }
                    )
                    MATCH (
                        b:Class {
                            name:$target,
                            repository_id:$repository_id
                        }
                    )
                    MERGE (a)-[:HAS_CLASS]->(b)
                    """,
                    "HAS_FUNCTION": """
                    MATCH (
                        a:File {
                            path:$source,
                            repository_id:$repository_id
                        }
                    )
                    MATCH (
                        b:Function {
                            qualified_name:$target,
                            repository_id:$repository_id
                        }
                    )
                    MERGE (a)-[:HAS_FUNCTION]->(b)
                    """,
                    "HAS_METHOD": """
                    MATCH (
                        a:Class {
                            name:$source,
                            repository_id:$repository_id
                        }
                    )
                    MATCH (
                        b:Function {
                            qualified_name:$target,
                            repository_id:$repository_id
                        }
                    )
                    MERGE (a)-[:HAS_METHOD]->(b)
                    """,
                    "CALLS": """
                    MATCH (
                        a:Function {
                            qualified_name:$source,
                            repository_id:$repository_id
                        }
                    )
                    MATCH (
                        b:Function {
                            qualified_name:$target,
                            repository_id:$repository_id
                        }
                    )
                    MERGE (a)-[:CALLS]->(b)
                    """,
                    "DEPENDS_ON": """
                    MATCH (
                        a:Class {
                            name:$source,
                            repository_id:$repository_id
                        }
                    )
                    MATCH (
                        b:Class {
                            name:$target,
                            repository_id:$repository_id
                        }
                    )
                    MERGE (a)-[:DEPENDS_ON]->(b)
                    """,
                    "IMPORTS": """
                    MATCH (
                        a:File {
                            path:$source,
                            repository_id:$repository_id
                        }
                    )
                    MATCH (
                        b:Import {
                            statement:$target,
                            repository_id:$repository_id
                        }
                    )
                    MERGE (a)-[:IMPORTS]->(b)
                    """,
                    "INHERITS": """
                    MATCH (
                        a:Class {
                            name:$source,
                            repository_id:$repository_id
                        }
                    )
                    MATCH (
                        b:Class {
                            name:$target,
                            repository_id:$repository_id
                        }
                    )
                    MERGE (a)-[:INHERITS]->(b)
                    """,
                }.get(relationship_type)

                if not query:
                    continue

                session.run(
                    query,
                    source=relationship.source,
                    target=relationship.target,
                    repository_id=repository_id,
                )

        print("Neo4j incremental graph update complete.")

    # =====================================================
    # Repository
    # =====================================================

    def _store_repository(
        self,
        session,
        graph,
        repository_id: str,
    ):
        if graph.repository is None:
            return

        session.run(
            """
            MERGE (
                r:Repository {
                    path:$path,
                    repository_id:$repository_id
                }
            )
            SET r.name=$name
            """,
            path=graph.repository.path,
            name=graph.repository.name,
            repository_id=repository_id,
        )

    # =====================================================
    # Folder
    # =====================================================

    def _store_folders(
        self,
        session,
        graph,
        repository_id: str,
    ):
        for folder in graph.folders.values():
            session.run(
                """
                MERGE (
                    f:Folder {
                        path:$path,
                        repository_id:$repository_id
                    }
                )
                SET f.name=$name
                """,
                path=folder.path,
                name=folder.name,
                repository_id=repository_id,
            )

    # =====================================================
    # File
    # =====================================================

    def _store_files(
        self,
        session,
        graph,
        repository_id: str,
    ):
        for file in graph.files.values():
            session.run(
                """
                MERGE (
                    f:File {
                        path:$path,
                        repository_id:$repository_id
                    }
                )
                SET
                    f.name=$name,
                    f.language=$language
                """,
                path=file.path,
                name=file.name,
                language=file.language,
                repository_id=repository_id,
            )

    # =====================================================
    # Imports
    # =====================================================

    def _store_imports(
        self,
        session,
        graph,
        repository_id: str,
    ):
        for imp in graph.imports.values():
            session.run(
                """
                MERGE (
                    i:Import {
                        statement:$statement,
                        repository_id:$repository_id
                    }
                )
                SET
                    i.module=$module,
                    i.alias=$alias,
                    i.file_path=$file_path
                """,
                statement=imp.statement,
                module=getattr(imp, "module", None),
                alias=getattr(imp, "alias", None),
                file_path=getattr(imp, "file_path", None),
                repository_id=repository_id,
            )

    # =====================================================
    # Classes
    # =====================================================

    def _store_classes(
        self,
        session,
        graph,
        repository_id: str,
    ):
        for cls in graph.classes.values():
            session.run(
                """
                MERGE (
                    c:Class {
                        name:$name,
                        repository_id:$repository_id
                    }
                )
                SET
                    c.qualified_name=$qualified_name,
                    c.file_path=$file_path,
                    c.visibility=$visibility,
                    c.base_classes=$base_classes,
                    c.decorators=$decorators,
                    c.start_line=$start_line,
                    c.end_line=$end_line,
                    c.code=$code
                """,
                name=cls.name,
                qualified_name=getattr(cls, "qualified_name", cls.name),
                file_path=cls.file_path,
                visibility=getattr(cls, "visibility", "public"),
                base_classes=serialize_for_neo4j(getattr(cls, "base_classes", [])),
                decorators=serialize_for_neo4j(getattr(cls, "decorators", [])),
                start_line=cls.start_line,
                end_line=cls.end_line,
                code=getattr(cls, "code", ""),
                repository_id=repository_id,
            )

    # =====================================================
    # Functions
    # =====================================================

    def _store_functions(
        self,
        session,
        graph,
        repository_id: str,
    ):
        for function in graph.functions.values():
            session.run(
                """
                MERGE (
                    f:Function {
                        qualified_name:$qualified_name,
                        repository_id:$repository_id
                    }
                )
                SET
                    f.name=$name,
                    f.file_path=$file_path,
                    f.class_name=$class_name,
                    f.is_method=$is_method,
                    f.is_async=$is_async,
                    f.visibility=$visibility,
                    f.is_static=$is_static,
                    f.is_classmethod=$is_classmethod,
                    f.parameters=$function_parameters,
                    f.returns=$returns,
                    f.calls=$calls,
                    f.dependencies=$dependencies,
                    f.decorators=$decorators,
                    f.start_line=$start_line,
                    f.end_line=$end_line,
                    f.code=$code
                """,
                qualified_name=function.qualified_name,
                name=function.name,
                file_path=function.file_path,
                class_name=function.class_name,
                is_method=function.is_method,
                is_async=function.is_async,
                visibility=function.visibility,
                is_static=function.is_static,
                is_classmethod=function.is_classmethod,
                function_parameters=serialize_for_neo4j(function.parameters),
                returns=serialize_for_neo4j(function.returns),
                calls=serialize_for_neo4j(function.calls),
                dependencies=serialize_for_neo4j(function.dependencies),
                decorators=serialize_for_neo4j(function.decorators),
                start_line=function.start_line,
                end_line=function.end_line,
                code=function.code,
                repository_id=repository_id,
            )

    # =====================================================
    # Routes
    # =====================================================

    def _store_routes(
        self,
        session,
        graph,
        repository_id: str,
    ):
        for route in graph.routes.values():
            session.run(
                """
                MERGE (
                    r:Route {
                        path:$path,
                        method:$method,
                        repository_id:$repository_id
                    }
                )
                SET
                    r.handler=$handler,
                    r.file_path=$file_path
                """,
                path=route.path,
                method=route.method,
                handler=route.handler,
                file_path=getattr(route, "file_path", None),
                repository_id=repository_id,
            )

    # =====================================================
    # Models
    # =====================================================

    def _store_models(
        self,
        session,
        graph,
        repository_id: str,
    ):
        for model in graph.models.values():
            session.run(
                """
                MERGE (
                    m:Model {
                        name:$name,
                        repository_id:$repository_id
                    }
                )
                SET
                    m.file_path=$file_path
                """,
                name=model.name,
                file_path=model.file_path,
                repository_id=repository_id,
            )

    # =====================================================
    # Relationships
    # =====================================================

    def _store_relationships(
        self,
        session,
        graph,
        repository_id: str,
    ):
        relationship_queries = {
            "HAS_FOLDER": """
            MATCH (
                a:Repository {
                    path:$source,
                    repository_id:$repository_id
                }
            )
            MATCH (
                b:Folder {
                    path:$target,
                    repository_id:$repository_id
                }
            )
            MERGE (a)-[:HAS_FOLDER]->(b)
            """,
            "HAS_FILE": """
            MATCH (
                a:Folder {
                    path:$source,
                    repository_id:$repository_id
                }
            )
            MATCH (
                b:File {
                    path:$target,
                    repository_id:$repository_id
                }
            )
            MERGE (a)-[:HAS_FILE]->(b)
            """,
            "HAS_CLASS": """
            MATCH (
                a:File {
                    path:$source,
                    repository_id:$repository_id
                }
            )
            MATCH (
                b:Class {
                    name:$target,
                    repository_id:$repository_id
                }
            )
            MERGE (a)-[:HAS_CLASS]->(b)
            """,
            "HAS_FUNCTION": """
            MATCH (
                a:File {
                    path:$source,
                    repository_id:$repository_id
                }
            )
            MATCH (
                b:Function {
                    qualified_name:$target,
                    repository_id:$repository_id
                }
            )
            MERGE (a)-[:HAS_FUNCTION]->(b)
            """,
            "HAS_METHOD": """
            MATCH (
                a:Class {
                    name:$source,
                    repository_id:$repository_id
                }
            )
            MATCH (
                b:Function {
                    qualified_name:$target,
                    repository_id:$repository_id
                }
            )
            MERGE (a)-[:HAS_METHOD]->(b)
            """,
            "CALLS": """
            MATCH (
                a:Function {
                    qualified_name:$source,
                    repository_id:$repository_id
                }
            )
            MATCH (
                b:Function {
                    qualified_name:$target,
                    repository_id:$repository_id
                }
            )
            MERGE (a)-[:CALLS]->(b)
            """,
            "DEPENDS_ON": """
            MATCH (
                a:Class {
                    name:$source,
                    repository_id:$repository_id
                }
            )
            MATCH (
                b:Class {
                    name:$target,
                    repository_id:$repository_id
                }
            )
            MERGE (a)-[:DEPENDS_ON]->(b)
            """,
            "IMPORTS": """
            MATCH (
                a:File {
                    path:$source,
                    repository_id:$repository_id
                }
            )
            MATCH (
                b:Import {
                    statement:$target,
                    repository_id:$repository_id
                }
            )
            MERGE (a)-[:IMPORTS]->(b)
            """,
            "INHERITS": """
            MATCH (
                a:Class {
                    name:$source,
                    repository_id:$repository_id
                }
            )
            MATCH (
                b:Class {
                    name:$target,
                    repository_id:$repository_id
                }
            )
            MERGE (a)-[:INHERITS]->(b)
            """,
        }

        for relationship in graph.relationships:
            query = relationship_queries.get(relationship.relationship_type)

            if not query:
                continue

            print(
                "STORING RELATIONSHIP:",
                relationship.relationship_type,
                "|",
                relationship.source,
                "->",
                relationship.target,
            )

            session.run(
                query,
                source=relationship.source,
                target=relationship.target,
                repository_id=repository_id,
            )