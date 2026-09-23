"""Detect drift between tdesktop's upstream api.tl and our last-seen snapshot.

This never touches `compiler/api/source/main_api.tl`: that file is hand-curated (it
comments out constructors marked "Parsed manually" / "Not used" instead of mirroring
upstream line for line), so a blind overwrite would corrupt it. Instead this compares
upstream against `compiler/api/upstream_snapshot/api.tl`, a plain copy of the last
version we looked at, and reports only what changed since then. A human still decides
which of those changes belong in the curated schema.

Run standalone to see the diff locally: `python .github/scripts/check_tl_schema.py`.
Set GITHUB_OUTPUT to also emit `changed=true|false` for the workflow to branch on.
"""

from __future__ import annotations

import difflib
import os
import pathlib
import sys
import urllib.request

UPSTREAM_URL = "https://raw.githubusercontent.com/telegramdesktop/tdesktop/dev/Telegram/SourceFiles/mtproto/scheme/api.tl"
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = REPO_ROOT / "compiler" / "api" / "upstream_snapshot" / "api.tl"
DIFF_OUTPUT_PATH = REPO_ROOT / "tl_schema_diff.txt"
# GitHub issue bodies cap out well above this, but a schema rewrite could in principle
#  produce a diff of any size, and there is no reason to test that ceiling in practice.
MAX_DIFF_CHARS = 50_000


def fetch_upstream() -> str:
    with urllib.request.urlopen(UPSTREAM_URL, timeout=30) as response:  # noqa: S310
        return response.read().decode("utf-8")


def main() -> int:
    upstream = fetch_upstream()
    previous = SNAPSHOT_PATH.read_text(encoding="utf-8") if SNAPSHOT_PATH.exists() else ""

    if upstream == previous:
        print("No upstream change since the last snapshot.")
        _set_output("changed", "false")
        return 0

    diff = "".join(
        difflib.unified_diff(
            previous.splitlines(keepends=True),
            upstream.splitlines(keepends=True),
            fromfile="compiler/api/upstream_snapshot/api.tl (last seen)",
            tofile="tdesktop dev api.tl (current)",
        )
    )

    issue_body = diff
    if len(issue_body) > MAX_DIFF_CHARS:
        issue_body = issue_body[:MAX_DIFF_CHARS] + "\n... (truncated; see the commit to the snapshot file for the full diff)\n"

    DIFF_OUTPUT_PATH.write_text(issue_body, encoding="utf-8")
    SNAPSHOT_PATH.write_text(upstream, encoding="utf-8")

    print(diff)
    _set_output("changed", "true")
    return 0


def _set_output(key: str, value: str) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        return
    with open(github_output, "a", encoding="utf-8") as fh:
        fh.write(f"{key}={value}\n")


if __name__ == "__main__":
    sys.exit(main())
