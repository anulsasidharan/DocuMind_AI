"""
RAG Pipeline — Documentation Q&A (legacy single-file blueprint).

Use modular code under src/, api/, pipelines/, scripts/ instead.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.rag_pipeline import query  # noqa: E402


if __name__ == "__main__":
    answer = query("What is this document about?")
    print(answer)
