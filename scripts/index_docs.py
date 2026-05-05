"""
Index markdown/text files or directories into Qdrant.

Usage (from project root, with PYTHONPATH=. or `pip install -e .`):

  python scripts/index_docs.py data/raw/gcp-docs-samples/README.md
  python scripts/index_docs.py data/raw/gcp-docs-samples
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import Settings
from src.rag_pipeline import index_documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Index paths into Qdrant")
    parser.add_argument(
        "paths",
        nargs="+",
        help="Files or directories containing .md / .txt",
    )
    parser.add_argument(
        "--collection",
        default=None,
        help="Override COLLECTION_NAME from env",
    )
    args = parser.parse_args()

    settings = Settings()
    if args.collection:
        settings = settings.model_copy(update={"collection_name": args.collection})

    n = index_documents(list(args.paths), settings=settings)
    print(f"Indexed {n} chunks into collection '{settings.collection_name}'.")


if __name__ == "__main__":
    main()
