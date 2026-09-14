from __future__ import annotations

from neo4j import GraphDatabase

from app.core.config import settings

import os


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

    def get_repository(
        self,
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (r:Repository)
            WHERE r.repository_id = $repository_id
            RETURN r
            LIMIT 1
            """

            with self.driver.session() as session:

                record = session.run(
                    query,
                    repository_id=repository_id,
                ).single()

                return (
                    record["r"]
                    if record
                    else None
                )

        # Existing behavior preserved

        query = """
        MATCH (r:Repository)
        RETURN r
        LIMIT 1
        """

        with self.driver.session() as session:

            record = session.run(
                query
            ).single()

            return (
                record["r"]
                if record
                else None
            )

    # =====================================================
    # Repository Structure
    # =====================================================

    def get_repository_structure(
        self,
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (r:Repository)
            WHERE r.repository_id = $repository_id

            MATCH (r)-[:HAS_FOLDER]->(folder)
            OPTIONAL MATCH (folder)-[:HAS_FILE]->(file)

            RETURN
                folder.name AS folder,
                collect(file.name) AS files

            ORDER BY folder
            """

            params = {
                "repository_id": repository_id
            }

        else:

            query = """
            MATCH (r:Repository)-[:HAS_FOLDER]->(folder)
            OPTIONAL MATCH (folder)-[:HAS_FILE]->(file)

            RETURN
                folder.name AS folder,
                collect(file.name) AS files

            ORDER BY folder
            """

            params = {}

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
            )

            return [
                dict(record)
                for record in result
            ]

    # =====================================================
    # File
    # =====================================================

    def get_file(
        self,
        file_path: str,
        repository_id: str | None = None,
    ):

        suffix_slash = "/" + file_path
        suffix_backslash = "\\" + file_path

        if repository_id:

            query = """
            MATCH (f:File)
            WHERE (
                f.path = $path
                OR f.name = $path
                OR f.path ENDS WITH $suffix_slash
                OR f.path ENDS WITH $suffix_backslash
            )
            AND f.repository_id = $repository_id
            RETURN f
            LIMIT 1
            """

            params = {
                "path": file_path,
                "suffix_slash": suffix_slash,
                "suffix_backslash": suffix_backslash,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (f:File)
            WHERE (
                f.path = $path
                OR f.name = $path
                OR f.path ENDS WITH $suffix_slash
                OR f.path ENDS WITH $suffix_backslash
            )
            RETURN f
            LIMIT 1
            """

            params = {
                "path": file_path,
                "suffix_slash": suffix_slash,
                "suffix_backslash": suffix_backslash,
            }

        with self.driver.session() as session:

            record = session.run(
                query,
                **params,
            ).single()

            return (
                record["f"]
                if record
                else None
            )

    # =====================================================
    # File By Name
    # =====================================================

    def get_file_by_name(
        self,
        file_name: str,
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (f:File {
                name:$name,
                repository_id:$repository_id
            })
            RETURN f
            LIMIT 1
            """

            params = {
                "name": file_name,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (f:File {name:$name})
            RETURN f
            LIMIT 1
            """

            params = {
                "name": file_name
            }

        with self.driver.session() as session:

            record = session.run(
                query,
                **params,
            ).single()

            return (
                record["f"]
                if record
                else None
            )

    # =====================================================
    # File Classes
    # =====================================================

    def get_file_classes(
        self,
        file_path: str,
        repository_id: str | None = None,
    ):

        suffix_slash = "/" + file_path
        suffix_backslash = "\\" + file_path

        if repository_id:

            query = """
            MATCH (f:File)
            WHERE (
                f.path = $path
                OR f.name = $path
                OR f.path ENDS WITH $suffix_slash
                OR f.path ENDS WITH $suffix_backslash
            )
            AND f.repository_id = $repository_id
            MATCH (f)-[:HAS_CLASS]->(c)

            RETURN c.name AS class
            """

            params = {
                "path": file_path,
                "suffix_slash": suffix_slash,
                "suffix_backslash": suffix_backslash,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (f:File)
            WHERE (
                f.path = $path
                OR f.name = $path
                OR f.path ENDS WITH $suffix_slash
                OR f.path ENDS WITH $suffix_backslash
            )
            MATCH (f)-[:HAS_CLASS]->(c)

            RETURN c.name AS class
            """

            params = {
                "path": file_path,
                "suffix_slash": suffix_slash,
                "suffix_backslash": suffix_backslash,
            }

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
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
        repository_id: str | None = None,
    ):

        suffix_slash = "/" + file_path
        suffix_backslash = "\\" + file_path

        if repository_id:

            query = """
            MATCH (f:File)
            WHERE (
                f.path = $path
                OR f.name = $path
                OR f.path ENDS WITH $suffix_slash
                OR f.path ENDS WITH $suffix_backslash
            )
            AND f.repository_id = $repository_id
            MATCH (f)-[:HAS_FUNCTION]->(fn)

            RETURN fn.name AS function
            """

            params = {
                "path": file_path,
                "suffix_slash": suffix_slash,
                "suffix_backslash": suffix_backslash,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (f:File)
            WHERE (
                f.path = $path
                OR f.name = $path
                OR f.path ENDS WITH $suffix_slash
                OR f.path ENDS WITH $suffix_backslash
            )
            MATCH (f)-[:HAS_FUNCTION]->(fn)

            RETURN fn.name AS function
            """

            params = {
                "path": file_path,
                "suffix_slash": suffix_slash,
                "suffix_backslash": suffix_backslash,
            }

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
            )

            return [
                record["function"]
                for record in result
            ]


    # =====================================================
    # Function
    # =====================================================

    def get_function(
        self,
        function_name: str,
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (f:Function)
            WHERE
                (
                    f.name = $name
                    OR f.qualified_name = $name
                )
                AND f.repository_id = $repository_id

            RETURN f
            LIMIT 1
            """

            params = {
                "name": function_name,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (f:Function)
            WHERE
                f.name = $name
                OR f.qualified_name = $name

            RETURN f
            LIMIT 1
            """

            params = {
                "name": function_name,
            }

        with self.driver.session() as session:

            record = session.run(
                query,
                **params,
            ).single()

            return (
                record["f"]
                if record
                else None
            )

    # =====================================================
    # Class
    # =====================================================

    def get_class(
        self,
        class_name: str,
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (c:Class {name:$name})
            WHERE c.repository_id = $repository_id
            RETURN c
            LIMIT 1
            """

            params = {
                "name": class_name,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (c:Class {name:$name})
            RETURN c
            LIMIT 1
            """

            params = {
                "name": class_name
            }

        with self.driver.session() as session:

            record = session.run(
                query,
                **params,
            ).single()

            return (
                record["c"]
                if record
                else None
            )

    # =====================================================
    # Class Methods
    # =====================================================

    def get_class_methods(
        self,
        class_name: str,
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (
                c:Class {
                    name:$name,
                    repository_id:$repository_id
                }
            )-[:HAS_METHOD]->(f)

            RETURN f.name AS method
            """

            params = {
                "name": class_name,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (c:Class {name:$name})-[:HAS_METHOD]->(f)

            RETURN f.name AS method
            """

            params = {
                "name": class_name
            }

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
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
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (c:Class)
            WHERE (c.name = $name OR c.qualified_name = $name)
            AND c.repository_id = $repository_id
            MATCH (c)-[:INHERITS]->(parent)

            RETURN coalesce(parent.name, parent.qualified_name) AS parent
            """

            params = {
                "name": class_name,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (c:Class)
            WHERE c.name = $name OR c.qualified_name = $name
            MATCH (c)-[:INHERITS]->(parent)

            RETURN coalesce(parent.name, parent.qualified_name) AS parent
            """

            params = {
                "name": class_name
            }

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
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
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (c:Class)
            WHERE (c.name = $name OR c.qualified_name = $name)
            AND c.repository_id = $repository_id
            MATCH (child)-[:INHERITS]->(c)

            RETURN coalesce(child.name, child.qualified_name) AS child
            """

            params = {
                "name": class_name,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (c:Class)
            WHERE c.name = $name OR c.qualified_name = $name
            MATCH (child)-[:INHERITS]->(c)

            RETURN coalesce(child.name, child.qualified_name) AS child
            """

            params = {
                "name": class_name
            }

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
            )

            return [
                record["child"]
                for record in result
            ]

    # =====================================================
    # Function Calls
    # =====================================================

    def get_function_calls(
        self,
        qualified_name: str,
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (f:Function)
            WHERE
                (
                    f.name = $name
                    OR f.qualified_name = $name
                )
                AND f.repository_id = $repository_id

            MATCH (f)-[:CALLS]->(called)

            RETURN coalesce(called.name, called.qualified_name) AS function
            """

            params = {
                "name": qualified_name,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (f:Function)
            WHERE
                f.name = $name
                OR f.qualified_name = $name

            MATCH (f)-[:CALLS]->(called)

            RETURN coalesce(called.name, called.qualified_name) AS function
            """

            params = {
                "name": qualified_name
            }

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
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
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (f:Function)
            WHERE
                (
                    f.name = $name
                    OR f.qualified_name = $name
                )
                AND f.repository_id = $repository_id

            MATCH (caller:Function)-[:CALLS]->(f)

            RETURN coalesce(caller.name, caller.qualified_name) AS function
            """

            params = {
                "name": qualified_name,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (f:Function)
            WHERE
                f.name = $name
                OR f.qualified_name = $name

            MATCH (caller:Function)-[:CALLS]->(f)

            RETURN coalesce(caller.name, caller.qualified_name) AS function
            """

            params = {
                "name": qualified_name
            }

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
            )

            rows = [
                record["function"]
                for record in result
            ]

        print(
            "\n========== CALLED BY =========="
        )

        print(
            "Target:",
            qualified_name,
        )

        print(
            "CALLERS:",
            rows,
        )

        print(
            "================================\n"
        )

        return rows

    # =====================================================
    # Imports
    # =====================================================

    def get_imports(
        self,
        file_path: str,
        repository_id: str | None = None,
    ):

        suffix_slash = "/" + file_path
        suffix_backslash = "\\" + file_path

        if repository_id:

            query = """
            MATCH (f:File)
            WHERE (
                f.path = $path
                OR f.name = $path
                OR f.path ENDS WITH $suffix_slash
                OR f.path ENDS WITH $suffix_backslash
            )
            AND f.repository_id = $repository_id
            MATCH (f)-[:IMPORTS]->(i:Import)

            RETURN i.statement AS import_statement
            """

            params = {
                "path": file_path,
                "suffix_slash": suffix_slash,
                "suffix_backslash": suffix_backslash,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (f:File)
            WHERE (
                f.path = $path
                OR f.name = $path
                OR f.path ENDS WITH $suffix_slash
                OR f.path ENDS WITH $suffix_backslash
            )
            MATCH (f)-[:IMPORTS]->(i:Import)

            RETURN i.statement AS import_statement
            """

            params = {
                "path": file_path,
                "suffix_slash": suffix_slash,
                "suffix_backslash": suffix_backslash,
            }

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
            )

            return [
                record["import_statement"]
                for record in result
            ]

    # =====================================================
    # Files Importing A File
    # =====================================================

    def get_files_importing(
        self,
        file_name: str,
        repository_id: str | None = None,
    ):

        print(
            "\n========== GET FILES IMPORTING =========="
        )

        print(
            "SEARCHING FOR:",
            file_name,
        )

        filename = os.path.basename(
            file_name
        )

        module_name = os.path.splitext(
            filename
        )[0]

        print(
            "FILENAME:",
            filename,
        )

        print(
            "SEARCHING MODULE:",
            module_name,
        )

        if repository_id:

            query = """
            MATCH (
                f:File {
                    repository_id:$repository_id
                }
            )-[:IMPORTS]->(i:Import)

            WHERE
                toLower(i.statement) CONTAINS toLower($module_name)

                OR (
                    i.module IS NOT NULL
                    AND toLower(i.module) CONTAINS toLower($module_name)
                )

            RETURN f.path AS file
            ORDER BY file
            """

            params = {
                "module_name": module_name,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (f:File)-[:IMPORTS]->(i:Import)

            WHERE
                toLower(i.statement) CONTAINS toLower($module_name)

                OR (
                    i.module IS NOT NULL
                    AND toLower(i.module) CONTAINS toLower($module_name)
                )

            RETURN f.path AS file
            ORDER BY file
            """

            params = {
                "module_name": module_name
            }

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
            )

            rows = [
                record["file"]
                for record in result
            ]

        print(
            "FOUND IMPORTERS:",
            rows,
        )

        print(
            "========================================\n"
        )

        return rows

    # =====================================================
    # Class Dependencies
    # =====================================================

    def get_class_dependencies(
        self,
        class_name: str,
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (c)
            WHERE (c.name = $name OR c.qualified_name = $name)
            AND c.repository_id = $repository_id
            MATCH (c)-[:DEPENDS_ON]->(dependency)

            RETURN coalesce(dependency.name, dependency.qualified_name, dependency.path) AS dependency
            """

            params = {
                "name": class_name,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (c)
            WHERE c.name = $name OR c.qualified_name = $name
            MATCH (c)-[:DEPENDS_ON]->(dependency)

            RETURN coalesce(dependency.name, dependency.qualified_name, dependency.path) AS dependency
            """

            params = {
                "name": class_name
            }

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
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
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (dependency)
            WHERE (dependency.name = $name OR dependency.qualified_name = $name)
            AND (dependency.repository_id = $repository_id OR dependency.repository_id IS NULL)
            MATCH (cls)-[:DEPENDS_ON]->(dependency)

            RETURN coalesce(cls.name, cls.qualified_name, cls.path) AS dependent
            """

            params = {
                "name": class_name,
                "repository_id": repository_id,
            }

        else:

            query = """
            MATCH (dependency)
            WHERE dependency.name = $name OR dependency.qualified_name = $name
            MATCH (cls)-[:DEPENDS_ON]->(dependency)

            RETURN coalesce(cls.name, cls.qualified_name, cls.path) AS dependent
            """

            params = {
                "name": class_name
            }

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
            )

            return [
                record["dependent"]
                for record in result
            ]

    # =====================================================
    # Graph Statistics
    # =====================================================

    def get_graph_statistics(
        self,
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (n)
            WHERE n.repository_id = $repository_id

            WITH
                count(
                    CASE
                        WHEN n:File THEN 1
                    END
                ) AS files,

                count(
                    CASE
                        WHEN n:Class THEN 1
                    END
                ) AS classes,

                count(
                    CASE
                        WHEN n:Function THEN 1
                    END
                ) AS functions

            OPTIONAL MATCH (
                source
            )-[r]->(
                target
            )

            WHERE
                source.repository_id = $repository_id

            RETURN
                files,
                classes,
                functions,
                count(r) AS relationships
            """

            params = {
                "repository_id": repository_id
            }

        else:

            query = """
            MATCH (n)

            WITH
                count(
                    CASE
                        WHEN n:File THEN 1
                    END
                ) AS files,

                count(
                    CASE
                        WHEN n:Class THEN 1
                    END
                ) AS classes,

                count(
                    CASE
                        WHEN n:Function THEN 1
                    END
                ) AS functions

            OPTIONAL MATCH ()-[r]->()

            RETURN
                files,
                classes,
                functions,
                count(r) AS relationships
            """

            params = {}

        with self.driver.session() as session:

            record = session.run(
                query,
                **params,
            ).single()

            if not record:

                return {
                    "files": 0,
                    "classes": 0,
                    "functions": 0,
                    "relationships": 0,
                }

            return {
                "files": record["files"],
                "classes": record["classes"],
                "functions": record["functions"],
                "relationships": record["relationships"],
            }

    # =====================================================
    # Repository Dependency Graph
    # =====================================================

    def get_dependency_graph(
        self,
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (source)-[r]->(target)

            WHERE
                source.repository_id = $repository_id

            RETURN
                elementId(source) AS source_id,
                labels(source)[0] AS source_type,
                coalesce(
                    source.name,
                    source.qualified_name,
                    source.path
                ) AS source,
                type(r) AS relationship,
                elementId(target) AS target_id,
                labels(target)[0] AS target_type,
                coalesce(
                    target.name,
                    target.qualified_name,
                    target.path
                ) AS target

            ORDER BY source, target
            """

            params = {
                "repository_id": repository_id
            }

        else:

            query = """
            MATCH (source)-[r]->(target)

            RETURN
                elementId(source) AS source_id,
                labels(source)[0] AS source_type,
                coalesce(
                    source.name,
                    source.qualified_name,
                    source.path
                ) AS source,
                type(r) AS relationship,
                elementId(target) AS target_id,
                labels(target)[0] AS target_type,
                coalesce(
                    target.name,
                    target.qualified_name,
                    target.path
                ) AS target

            ORDER BY source, target
            """

            params = {}

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
            )

            records = [
                dict(record)
                for record in result
            ]

        print(
            "\n========== DEPENDENCY GRAPH DEBUG =========="
        )

        print(
            "Repository ID:",
            repository_id,
        )

        print(
            "Dependency relationships:",
            len(records),
        )

        if records:

            print(
                "First relationship:",
                records[0],
            )

        else:

            print(
                "NO DEPENDENCY RELATIONSHIPS FOUND"
            )

        print(
            "============================================\n"
        )

        return records

    # =====================================================
    # DEBUG FUNCTIONS
    # =====================================================

    def debug_functions(
        self,
        repository_id: str | None = None,
    ):

        if repository_id:

            query = """
            MATCH (f:Function)
            WHERE f.repository_id = $repository_id

            RETURN
                f.name AS name,
                f.qualified_name AS qualified_name

            ORDER BY name
            """

            params = {
                "repository_id": repository_id
            }

        else:

            query = """
            MATCH (f:Function)

            RETURN
                f.name AS name,
                f.qualified_name AS qualified_name

            ORDER BY name
            """

            params = {}

        with self.driver.session() as session:

            result = session.run(
                query,
                **params,
            )

            rows = [
                dict(record)
                for record in result
            ]

        print(
            "\n========== NEO4J FUNCTIONS =========="
        )

        for row in rows:
            print(row)

        print(
            "TOTAL FUNCTIONS:",
            len(rows),
        )

        print(
            "====================================\n"
        )

        return rows