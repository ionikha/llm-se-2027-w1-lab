"""Read one GitHub issue JSON object and print its triage record."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence
from urllib.parse import urlparse

from pydantic import ValidationError

from triage.extract import triage_issue
from triage.models import GitHubIssue


def repository_from_url(url: str | None) -> str | None:
    if url is None:
        return None
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if parsed.hostname != "github.com" or len(parts) < 2:
        return None
    return "/".join(parts[:2])


def read_issue(source: str) -> GitHubIssue:
    if source == "-":
        payload = json.load(sys.stdin)
    else:
        with Path(source).open(encoding="utf-8") as issue_file:
            payload = json.load(issue_file)
    if not isinstance(payload, dict):
        raise ValueError("input must be one GitHub issue JSON object")
    return GitHubIssue.model_validate(payload)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "issue_json",
        nargs="?",
        default="-",
        help="path to one issue JSON object, or - for stdin (default)",
    )
    parser.add_argument(
        "--repo",
        help="repository key/name when it is not present in the issue payload or URL",
    )
    args = parser.parse_args(argv)

    try:
        issue = read_issue(args.issue_json)
        repository = args.repo or issue.repo or repository_from_url(issue.url)
        if not repository:
            raise ValueError("repository is unknown; provide it with --repo")
        record = triage_issue(issue, repository)
    except (OSError, json.JSONDecodeError, ValidationError, ValueError, RuntimeError) as exc:
        print(f"triage error: {exc}", file=sys.stderr)
        return 2

    print(record.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())