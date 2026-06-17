import os

NOVELTY_THRESHOLD               = 0.35
TOP_K_COMPARISONS               = 5
EMBEDDING_MODEL                 = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIM                   = 384
COLLECTION_NAME                 = "osiris_research_corpus"
QDRANT_VECTOR_NAME              = "repo_embedding"
MAX_DOC_SCORE                   = 100
GATE_APPROVAL_THRESHOLD         = 0.60
MIN_STARS_PREFILTER             = 50
MIN_README_PREFILTER            = 200


DUPLICATE_SIMILARITY_THRESHOLD  = 0.94
WRAPPER_SIMILARITY_THRESHOLD    = 0.85

HYBRID_WEIGHTS = {
    "readme":       0.40,
    "description":  0.25,
    "topics":       0.20,
    "category":     0.10,
    "language":     0.05,
}

NOVELTY_WEIGHTS = {
    "semantic":   0.60,
    "tech_stack": 0.20,
    "category":   0.10,
    "activity":   0.10,
}


# The below configuration is for the repository embedding pipeline. Environment
# variables are used here so deployments can change models, chunking, and Qdrant
# targets without editing source code.
REPOSITORY_EMBEDDING_MODEL = EMBEDDING_MODEL
REPOSITORY_EMBEDDING_DIM = EMBEDDING_DIM
REPOSITORY_EMBEDDING_VERSION = os.getenv("REPOSITORY_EMBEDDING_VERSION", "repo-embedding-v1")
README_CHUNK_CHARS = int(os.getenv("README_CHUNK_CHARS", "2500"))
README_CHUNK_OVERLAP_CHARS = int(os.getenv("README_CHUNK_OVERLAP_CHARS", "250"))

REPO_TOWER_WEIGHTS = {
    "readme": 0.60,
    "metadata": 0.25,
    "topics": 0.15,
}

# The below Qdrant settings are for collection bootstrap, indexing, and CLI
# validation commands.
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or None
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", COLLECTION_NAME)
QDRANT_DISTANCE = os.getenv("QDRANT_DISTANCE", "Cosine")
QDRANT_PAYLOAD_INDEX_FIELDS = [
    "repo_id",
    "primary_language",
    "category",
    "discovery_category",
    "discovery_band",
    "star_count",
    "updated_at",
    "pushed_at",
]
