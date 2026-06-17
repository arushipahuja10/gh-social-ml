"""Run qualitative semantic retrieval queries against repository embeddings."""

from __future__ import annotations

import argparse
import logging
import os

from dotenv import load_dotenv

from ingestion.config import QDRANT_API_KEY, QDRANT_COLLECTION_NAME, QDRANT_URL
from ingestion.embedding_pipeline import RepositoryEmbeddingPipeline
from ingestion.qdrant_store import QdrantRepositoryStore
from ingestion.repository_embedding import RepositoryEmbeddingConfig


DEFAULT_QUERIES = [
    "large language model framework",
    "frontend ui library",
    "database ORM",
    "computer vision",
    "devops kubernetes",
]


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run semantic text-query retrieval tests.")
    parser.add_argument("queries", nargs="*", help="Optional custom queries")
    parser.add_argument("--top-k", type=int, default=10, help="Results per query")
    parser.add_argument("--qdrant-url", default=QDRANT_URL, help="Qdrant URL")
    parser.add_argument("--qdrant-api-key", default=QDRANT_API_KEY, help="Qdrant API key")
    parser.add_argument("--collection", default=QDRANT_COLLECTION_NAME, help="Qdrant collection name")
    parser.add_argument("--model", default=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"), help="SentenceTransformer model")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = _parse_args()
    _setup_logging(args.log_level)

    config = RepositoryEmbeddingConfig(model_name=args.model)
    store = QdrantRepositoryStore(
        url=args.qdrant_url,
        api_key=args.qdrant_api_key,
        collection_name=args.collection,
        vector_size=config.embedding_dim,
    )
    pipeline = RepositoryEmbeddingPipeline(config=config, store=store)
    queries = args.queries or DEFAULT_QUERIES

    # The below loop is for quick qualitative inspection of whether natural
    # language intents retrieve repositories in the expected semantic area.
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 78)
        for index, match in enumerate(pipeline.search(query, limit=args.top_k), 1):
            payload = match.get("payload", {})
            category = payload.get("discovery_category") or payload.get("category") or "Unknown"
            print(f"{index:>2}. score={match['score']:.4f}  repo={match.get('repo_id')}  category={category}")


if __name__ == "__main__":
    main()
