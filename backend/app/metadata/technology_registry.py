"""
Technology Registry

Maps imported Python modules to technologies used
by the repository.

This registry is used by RepositoryProfiler to detect

- Frameworks
- Databases
- AI Frameworks
- Vector Databases
- Web Frameworks
- ORMs
- Testing Frameworks
"""

"""
Technology Registry

Maps imported Python modules to technologies used
by the repository.

This registry is used by RepositoryProfiler to detect:

- Frameworks
- Databases
- AI / LLM Frameworks
- Agent Frameworks
- Vector Databases
- LLM Providers
- Web Frameworks
- ORMs
- Testing Frameworks
"""

TECHNOLOGY_REGISTRY = {

    # =====================================================
    # Web Frameworks
    # =====================================================

    "fastapi": {
        "name": "FastAPI",
        "category": "Web Framework",
    },

    "flask": {
        "name": "Flask",
        "category": "Web Framework",
    },

    "django": {
        "name": "Django",
        "category": "Web Framework",
    },

    # =====================================================
    # AI / LLM Frameworks
    # =====================================================

    "langchain": {
        "name": "LangChain",
        "category": "LLM Framework",
    },

    "langchain_core": {
        "name": "LangChain",
        "category": "LLM Framework",
    },

    "langchain_chroma": [
        {
            "name": "LangChain Chroma",
            "category": "LLM Framework",
        },
        {
            "name": "ChromaDB",
            "category": "Vector Database",
        },
    ],

    "langchain_huggingface": {
        "name": "LangChain HuggingFace",
        "category": "LLM Framework",
    },

    "langchain_groq": [
        {
            "name": "LangChain Groq",
            "category": "LLM Framework",
        },
        {
            "name": "Groq",
            "category": "LLM Provider",
        },
    ],

    "sentence_transformers": {
        "name": "Sentence Transformers",
        "category": "LLM Framework",
    },

    # =====================================================
    # Agent Frameworks
    # =====================================================

    "langgraph": {
        "name": "LangGraph",
        "category": "LLM Framework",
    },

    # =====================================================
    # LLM Providers
    # =====================================================

    "openai": {
        "name": "OpenAI",
        "category": "LLM Provider",
    },

    "google": {
        "name": "Google GenAI",
        "category": "LLM Provider",
    },

    "groq": {
        "name": "Groq",
        "category": "LLM Provider",
    },

    # =====================================================
    # HuggingFace
    # =====================================================

    "transformers": {
        "name": "HuggingFace Transformers",
        "category": "LLM Framework",
    },

    # =====================================================
    # Vector Databases
    # =====================================================

    "chromadb": {
        "name": "ChromaDB",
        "category": "Vector Database",
    },

    "faiss": {
        "name": "FAISS",
        "category": "Vector Database",
    },

    "pinecone": {
        "name": "Pinecone",
        "category": "Vector Database",
    },

    "weaviate": {
        "name": "Weaviate",
        "category": "Vector Database",
    },

    # =====================================================
    # Graph Databases
    # =====================================================

    "neo4j": {
        "name": "Neo4j",
        "category": "Graph Database",
    },

    # =====================================================
    # Databases
    # =====================================================

    "redis": {
        "name": "Redis",
        "category": "Database",
    },

    "sqlite3": {
        "name": "SQLite",
        "category": "Database",
    },

    "pymongo": {
        "name": "MongoDB",
        "category": "Database",
    },

    "sqlalchemy": {
        "name": "SQLAlchemy",
        "category": "ORM",
    },

    # =====================================================
    # Testing
    # =====================================================

    "pytest": {
        "name": "PyTest",
        "category": "Testing",
    },

    "unittest": {
        "name": "unittest",
        "category": "Testing",
    },

    # =====================================================
    # Async
    # =====================================================

    "asyncio": {
        "name": "AsyncIO",
        "category": "Concurrency",
    },

    # =====================================================
    # Data Science
    # =====================================================

    "numpy": {
        "name": "NumPy",
        "category": "Scientific Computing",
    },

    "pandas": {
        "name": "Pandas",
        "category": "Data Analysis",
    },
}