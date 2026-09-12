#!/usr/bin/env python
"""
Standalone script to ingest documents without going through the CLI.
Useful for cron jobs / scheduled re-indexing.

Usage:
    python scripts/ingest_documents.py [--force]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag_pipeline import ingest_documents

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    n = ingest_documents(force=args.force)
    print(f"Ingested {n} new chunk(s).")
