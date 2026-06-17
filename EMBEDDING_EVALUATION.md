# Embedding Evaluation

The below scripts are for measuring repository embedding quality after the
acquisition and Qdrant indexing pipeline has run.

## Start Qdrant

```powershell
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

Optional environment variables:

```powershell
$env:QDRANT_URL="http://localhost:6333"
$env:QDRANT_COLLECTION_NAME="osiris_research_corpus"
$env:EMBEDDING_MODEL="all-MiniLM-L6-v2"
```

## Index Repositories

The below command is for running discovery, enrichment, filtering, embedding,
and Qdrant indexing in one flow.

```powershell
python main.py --limit 50 --batch-size 10
```

Use `--no-index-qdrant` only when you want acquisition and filtering without
vector persistence.

## Evaluate Repository Embeddings

The below command is for evaluating vectors that already exist in Qdrant.

```powershell
python evaluate_embeddings.py --sample-size 50 --query-count 10 --top-k 10
```

The below command is for indexing a local approved repository payload JSON file
before running the evaluation.

```powershell
python evaluate_embeddings.py --corpus-json staged_repositories.json --sample-size 50
```

The evaluation prints repository nearest neighbors, same-category and
cross-category similarity, clustering quality, vector distribution statistics,
retrieval consistency, qualitative examples, and tower-weight recommendations.

## Run Qualitative Retrieval Tests

The below command is for checking natural-language retrieval behavior.

```powershell
python retrieval_test.py
```

Custom queries can be passed directly:

```powershell
python retrieval_test.py "python web framework" "vector database client"
```
