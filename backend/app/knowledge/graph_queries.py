from __future__ import annotations

from neo4j import GraphDatabase

from app.core.config import settings


class GraphQueries:
    """
    Repository Knowledge Graph Queries.
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
    # Repository
    # =====================================================

    def get_repository(self):

        query = """
        MATCH (r:Repository)
        RETURN r
        LIMIT 1
        """

        with self.driver.session() as session:

            record = session.run(query).single()

            return record["r"] if record else None

    # =====================================================
    # Repository Structure
    # =====================================================

    def get_repository_structure(self):

        query = """
        MATCH (r:Repository)-[:HAS_FOLDER]->(folder)
        OPTIONAL MATCH (folder)-[:HAS_FILE]->(file)

        RETURN
            folder.name AS folder,
            collect(file.name) AS files

        ORDER BY folder
        """

        with self.driver.session() as session:

            result = session.run(query)

            return [dict(record) for record in result]

    # =====================================================
    # File
    # =====================================================

    def get_file(
        self,
        file_path: str,
    ):

        query = """
        MATCH (f:File {path:$path})
        RETURN f
        """

        with self.driver.session() as session:

            record = session.run(
                query,
                path=file_path,
            ).single()

            return record["f"] if record else None

    # =====================================================
    # File Classes
    # =====================================================

    def get_file_classes(
        self,
        file_path: str,
    ):

        query = """
        MATCH (f:File {path:$path})-[:HAS_CLASS]->(c)

        RETURN c.name AS class
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                path=file_path,
            )

            return [

                record["class"]

                for record in result

            ]

    # =====================================================
    # File Functions
    # =====================================================

    def get_file_functions(
        self,
        file_path: str,
    ):

        query = """
        MATCH (f:File {path:$path})-[:HAS_FUNCTION]->(fn)

        RETURN fn.name AS function
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                path=file_path,
            )

            return [

                record["function"]

                for record in result

            ]

    # =====================================================
    # Class
    # =====================================================

    def get_class(
        self,
        class_name: str,
    ):

        query = """
        MATCH (c:Class {name:$name})

        RETURN c
        """

        with self.driver.session() as session:

            record = session.run(
                query,
                name=class_name,
            ).single()

            return record["c"] if record else None

    # =====================================================
    # Class Methods
    # =====================================================

    def get_class_methods(
        self,
        class_name: str,
    ):

        query = """
        MATCH (c:Class {name:$name})-[:HAS_METHOD]->(f)

        RETURN f.name AS method
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                name=class_name,
            )

            return [

                record["method"]

                for record in result

            ]

    # =====================================================
    # Parent Classes
    # =====================================================

    def get_parent_classes(
        self,
        class_name: str,
    ):

        query = """
        MATCH (c:Class {name:$name})-[:INHERITS]->(parent)

        RETURN parent.name AS parent
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                name=class_name,
            )

            return [

                record["parent"]

                for record in result

            ]

    # =====================================================
    # Child Classes
    # =====================================================

    def get_child_classes(
        self,
        class_name: str,
    ):

        query = """
        MATCH (child)-[:INHERITS]->(c:Class {name:$name})

        RETURN child.name AS child
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                name=class_name,
            )

            return [

                record["child"]

                for record in result

            ]

    # =====================================================
    # Function
    # =====================================================

    def get_function(
        self,
        qualified_name: str,
    ):

        query = """
        MATCH (f:Function {name:$name})

        RETURN f
        """

        with self.driver.session() as session:

            record = session.run(
                query,
                name=qualified_name,
            ).single()

            return record["f"] if record else None

    # =====================================================
    # Function Calls
    # =====================================================

    def get_function_calls(
        self,
        qualified_name: str,
    ):

        query = """
        MATCH (f:Function {name:$name})-[:CALLS]->(called)

        RETURN called.name AS function
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                name=qualified_name,
            )

            return [

                record["function"]

                for record in result

            ]

    # =====================================================
    # Called By
    # =====================================================

    def get_called_by(
        self,
        qualified_name: str,
    ):

        query = """
        MATCH (caller)-[:CALLS]->(f:Function {name:$name})

        RETURN caller.name AS function
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                name=qualified_name,
            )

            return [

                record["function"]

                for record in result

            ]
# =====================================================
# Imports
# =====================================================

def get_imports(
    self,
    file_path: str,
):

    query = """
    MATCH (f:File {path:$path})-[:IMPORTS]->(i:Import)

    RETURN i.statement AS import_statement
    """

    with self.driver.session() as session:

        result = session.run(
            query,
            path=file_path,
        )

        return [

            record["import_statement"]

            for record in result

        ]


    # =====================================================
# Class Dependencies
# =====================================================

def get_class_dependencies(
    self,
    class_name: str,
):

    query = """
    MATCH (c:Class {name:$name})-[:DEPENDS_ON]->(dependency)

    RETURN dependency.name AS dependency
    """

    with self.driver.session() as session:

        result = session.run(
            query,
            name=class_name,
        )

        return [

            record["dependency"]

            for record in result

        ]


    # =====================================================
# Dependent Classes
# =====================================================

def get_dependent_classes(
    self,
    class_name: str,
):

    query = """
    MATCH (dependency:Class {name:$name})<-[:DEPENDS_ON]-(cls)

    RETURN cls.name AS dependent
    """

    with self.driver.session() as session:

        result = session.run(
            query,
            name=class_name,
        )

        return [

            record["dependent"]

            for record in result

        ]

    