"""
Download a GCP-flavored documentation corpus for local indexing.

Default: shallow clone of GoogleCloudPlatform/python-docs-samples into data/raw/.

Usage:
  python scripts/download_gcp_docs.py
  python scripts/download_gcp_docs.py --target data/raw/my-samples
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = ROOT / "data" / "raw" / "gcp-docs-samples"
REPO = "https://github.com/GoogleCloudPlatform/python-docs-samples.git"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--target", type=Path, default=DEFAULT_TARGET, help="Clone destination")
    p.add_argument("--depth", type=int, default=1, help="git clone --depth (1=shallow)")
    args = p.parse_args()

    args.target.parent.mkdir(parents=True, exist_ok=True)
    if args.target.exists() and any(args.target.iterdir()):
        print(f"Target already exists and is non-empty: {args.target}", file=sys.stderr)
        print("Remove it or pick another --target.", file=sys.stderr)
        sys.exit(1)

    cmd = ["git", "clone", "--depth", str(args.depth), REPO, str(args.target)]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Cloned to {args.target}")
    print("Index with: python scripts/index_docs.py", args.target)


if __name__ == "__main__":
    main()
