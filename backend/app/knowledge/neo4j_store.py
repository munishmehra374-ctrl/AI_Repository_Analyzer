from __future__ import annotations

from neo4j import GraphDatabase

from app.core.config import settings


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
    # Public API
    # =====================================================

    def store_graph(
        self,
        graph,
    ):

        with self.driver.session() as session:

            self._store_repository(
                session,
                graph,
            )

            self._store_folders(
                session,
                graph,
            )

            self._store_files(
                session,
                graph,
            )

            self._store_imports(
                session,
                graph,
            )

            self._store_classes(
                session,
                graph,
            )

            self._store_functions(
                session,
                graph,
            )

            self._store_routes(
                session,
                graph,
            )

            self._store_models(
                session,
                graph,
            )

            self._store_relationships(
                session,
                graph,
            )

    # =====================================================
    # Repository
    # =====================================================

    def _store_repository(
        self,
        session,
        graph,
    ):

        if graph.repository is None:
            return

        session.run(
            """
            MERGE (r:Repository {path:$path})
            SET r.name=$name
            """,
            path=graph.repository.path,
            name=graph.repository.name,
        )

    # =====================================================
    # Folder
    # =====================================================

    def _store_folders(
        self,
        session,
        graph,
    ):

        for folder in graph.folders.values():

            session.run(
                """
                MERGE (f:Folder {path:$path})
                SET f.name=$name
                """,
                path=folder.path,
                name=folder.name,
            )

    # =====================================================
    # File
    # =====================================================

    def _store_files(
        self,
        session,
        graph,
    ):

        for file in graph.files.values():

            session.run(
                """
                MERGE (f:File {path:$path})
                SET
                    f.name=$name,
                    f.language=$language
                """,
                path=file.path,
                name=file.name,
                language=file.language,
            )

    # =====================================================
    # Imports
    # =====================================================

    def _store_imports(
        self,
        session,
        graph,
    ):

        for imp in graph.imports.values():

            session.run(
                """
                MERGE (i:Import {statement:$statement})
                SET
                    i.module=$module
                """,
                statement=imp.statement,
                module=getattr(
                    imp,
                    "module",
                    None,
                ),
            )

    # =====================================================
    # Classes
    # =====================================================

    def _store_classes(
        self,
        session,
        graph,
    ):

        for cls in graph.classes.values():

            session.run(
                """
                MERGE (c:Class {name:$name})

                SET
                    c.file_path=$file_path,
                    c.start_line=$start_line,
                    c.end_line=$end_line
                """,
                name=cls.name,
                file_path=cls.file_path,
                start_line=cls.start_line,
                end_line=cls.end_line,
            )

                # =====================================================
    # Functions
    # =====================================================

    def _store_functions(
        self,
        session,
        graph,
    ):

        for function in graph.functions.values():

            session.run(
                """
                MERGE (f:Function {
                    qualified_name:$qualified_name
                })

                SET
                    f.name=$name,
                    f.file_path=$file_path,
                    f.class_name=$class_name,
                    f.start_line=$start_line,
                    f.end_line=$end_line
                """,
                qualified_name=function.qualified_name,
                name=function.name,
                file_path=function.file_path,
                class_name=function.class_name,
                start_line=function.start_line,
                end_line=function.end_line,
            )

    # =====================================================
    # Routes
    # =====================================================

    def _store_routes(
        self,
        session,
        graph,
    ):

        for route in graph.routes.values():

            session.run(
                """
                MERGE (r:Route {
                    path:$path,
                    method:$method
                })

                SET
                    r.handler=$handler
                """,
                path=route.path,
                method=route.method,
                handler=route.handler,
            )
    # =====================================================
    # Models
    # =====================================================

    def _store_models(
        self,
        session,
        graph,
    ):

        for model in graph.models.values():

            session.run(
                """
                MERGE (m:Model {name:$name})

                SET
                    m.file_path=$file_path
                """,
                name=model.name,
                file_path=model.file_path,
            )

    # =====================================================
    # Relationships
    # =====================================================

    def _store_relationships(
        self,
        session,
        graph,
    ):

        relationship_queries = {

            "HAS_FOLDER":
            """
            MATCH (a:Repository {path:$source})
            MATCH (b:Folder {path:$target})
            MERGE (a)-[:HAS_FOLDER]->(b)
            """,

            "HAS_FILE":
            """
            MATCH (a:Folder {path:$source})
            MATCH (b:File {path:$target})
            MERGE (a)-[:HAS_FILE]->(b)
            """,

            "HAS_CLASS":
            """
            MATCH (a:File {path:$source})
            MATCH (b:Class {name:$target})
            MERGE (a)-[:HAS_CLASS]->(b)
            """,

            "HAS_FUNCTION":
            """
            MATCH (a:File {path:$source})
            MATCH (b:Function {qualified_name:$target})
            MERGE (a)-[:HAS_FUNCTION]->(b)
            """,

            "HAS_METHOD":
            """
            MATCH (a:Class {name:$source})
            MATCH (b:Function {qualified_name:$target})
            MERGE (a)-[:HAS_METHOD]->(b)
            """,

            "CALLS":
            """
            MATCH (a:Function {qualified_name:$source})
            MATCH (b:Function {qualified_name:$target})
            MERGE (a)-[:CALLS]->(b)
            """,

            "DEPENDS_ON":
            """
            MATCH (a:Class {name:$source})
            MATCH (b:Class {name:$target})
            MERGE (a)-[:DEPENDS_ON]->(b)
            """,

            "IMPORTS":
            """
            MATCH (a:File {path:$source})
            MATCH (b:Import {statement:$target})
            MERGE (a)-[:IMPORTS]->(b)
            """,

            "INHERITS":
            """
            MATCH (a:Class {name:$source})
            MATCH (b:Class {name:$target})
            MERGE (a)-[:INHERITS]->(b)
            """,
        }

        for relationship in graph.relationships:

            query = relationship_queries.get(
                relationship.relationship_type
            )

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
            )