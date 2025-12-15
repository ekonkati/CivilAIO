"""
Utility to fetch `myprd.txt` from a GitHub raw URL or confirm it exists locally.

Usage:
    python sync_myprd.py --url <raw_github_url>

If `--url` is omitted, the script only verifies that `myprd.txt` exists locally.
The goal is to keep an auditable, scripted way to pull the PRD text when a remote
URL is available (e.g., once a GitHub remote is configured in this environment).
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
TARGET = ROOT / "myprd.txt"


def fetch(url: str) -> None:
    try:
        with urllib.request.urlopen(url) as resp:  # nosec: B310 (runtime-provided URL)
            data = resp.read()
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to download myprd.txt from {url}: {exc}") from exc

    TARGET.write_bytes(data)
    print(f"Downloaded myprd.txt to {TARGET}")


def verify() -> None:
    if TARGET.exists():
        size = TARGET.stat().st_size
        print(f"Found existing myprd.txt ({size} bytes)")
    else:
        print("myprd.txt is not present locally. Provide --url to download it or place it in the repo root.")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sync myprd.txt into the repository")
    parser.add_argument("--url", help="Raw GitHub URL for myprd.txt")
    args = parser.parse_args(argv)

    if args.url:
        fetch(args.url)
    verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
