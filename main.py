"""
gh-social-ml  ·  Acquisition Pipeline
======================================

Stage 1 of the full architecture:
  Discovery  (GraphQL search across categories + maturity bands)
      ↓
  Enrichment  (metadata, languages, topics, README, star deltas)
      ↓
  EnrichmentResult list  (ready for Stage 2 — Feature Extraction)

Usage:
    python3 main.py [--limit N] [--batch-size N] [--log-level LEVEL]

Environment:
    GITHUB_TOKEN  — required, set in .env
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()


# ── Logging ───────────────────────────────────────────────────────────────────

def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )

logger = logging.getLogger("pipeline.acquisition")


# ══════════════════════════════════════════════════════════════════════════════
#  ACQUISITION
# ══════════════════════════════════════════════════════════════════════════════

def run_acquisition(
    token: str,
    *,
    limit: int = 100,
    batch_size: int = 10,
) -> list:
    """
    Discover and enrich GitHub repositories via GraphQL only.

    Returns a list of EnrichmentResult objects. Each carries:
      .repo_id          — "owner/repo"
      .payload          — Osiris-compatible dict (star_count, language, topics, …)
      .raw_repository   — raw GraphQL response fields
      .readme           — ReadmeDocument (clean_text, extracted_paragraphs, …)
      .topics           — list[str]
      .languages        — dict[str, int]  (language → bytes)
    """
    from acquisition.github_graphql_client import GitHubGraphQLClient
    from acquisition.github_discovery import GitHubDiscoveryEngine, DiscoveryConfig
    from acquisition.repository_enricher import RepositoryEnricher

    client   = GitHubGraphQLClient(token=token)
    config   = DiscoveryConfig(total_limit=limit + 20)   # small buffer to hit the target
    discovery = GitHubDiscoveryEngine(client, config=config)
    enricher  = RepositoryEnricher(graphql_client=client)

    # ── Step 1: Discovery ─────────────────────────────────────────────────────
    logger.info("Discovering repositories …")
    discovered = discovery.discover(limit=limit + 20)
    logger.info("Discovered %d candidate repos", len(discovered))

    # ── Step 2: Enrichment in batches ─────────────────────────────────────────
    logger.info("Enriching in batches of %d …", batch_size)
    enriched: list = []
    targets       = discovered[:limit]
    total_batches = (len(targets) + batch_size - 1) // batch_size

    for i in range(total_batches):
        batch = targets[i * batch_size : (i + 1) * batch_size]
        try:
            results = enricher.get_repositories_batch(batch)
            enriched.extend(results)
            logger.info(
                "  Batch %d/%d → +%d enriched  (total: %d)",
                i + 1, total_batches, len(results), len(enriched),
            )
        except Exception as exc:
            logger.warning("  Batch %d failed (%s). Falling back to one-by-one …", i + 1, exc)
            for repo in batch:
                full_name = repo if isinstance(repo, str) else repo.get("full_name", "")
                try:
                    r = enricher.enrich(full_name)
                    if r:
                        enriched.append(r)
                        logger.info("    ✓  %s", full_name)
                except Exception as exc2:
                    logger.warning("    ✗  %s: %s", full_name, exc2)

    logger.info("Acquisition complete — %d / %d repos enriched", len(enriched), limit)
    return enriched


# ── Summary printer ───────────────────────────────────────────────────────────

def _print_summary(enriched: list) -> None:
    if not enriched:
        logger.warning("No repos to display.")
        return

    sorted_repos = sorted(enriched, key=lambda r: r.payload.get("star_count", 0), reverse=True)

    width = 95
    print(f"\n{'═' * width}")
    print(f"  Acquisition complete — {len(enriched)} repos enriched")
    print(f"{'═' * width}")
    print(f"{'#':<4} {'Repository':<42} {'⭐ Stars':>8} {'Language':<14} {'README':>8}  Topics")
    print("─" * width)

    for i, r in enumerate(sorted_repos, 1):
        p = r.payload
        topics_str = ", ".join(p.get("topics", [])[:3]) or "—"
        print(
            f"{i:<4} {p['id']:<42} {p.get('star_count', 0):>8,}  "
            f"{p.get('primary_language', 'Unknown'):<14} "
            f"{p.get('readme_length', 0):>7,}c  {topics_str}"
        )

    print(f"{'═' * width}\n")


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="main.py",
        description="gh-social-ml acquisition pipeline: Discovery → Enrichment",
    )
    p.add_argument("--limit",      type=int, default=100,    help="Target number of repos (default: 100)")
    p.add_argument("--batch-size", type=int, default=10,     help="Enrichment batch size (default: 10)")
    p.add_argument("--log-level",  type=str, default="INFO", help="Logging level (default: INFO)")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token or token == "your_github_token_here":
        print("❌  ERROR: Set GITHUB_TOKEN in your .env file first.")
        sys.exit(1)

    _setup_logging(args.log_level)

    logger.info("╔══════════════════════════════════╗")
    logger.info("║  gh-social-ml  ·  Acquisition    ║")
    logger.info("╚══════════════════════════════════╝")

    enriched = run_acquisition(token, limit=args.limit, batch_size=args.batch_size)
    _print_summary(enriched)
