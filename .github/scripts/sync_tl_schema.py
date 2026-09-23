"""Sync `compiler/api/source/main_api.tl`'s body from upstream tdesktop api.tl.

That file is two things stitched together: a short hand-curated header (`boolFalse`,
`boolTrue`, `true`, `vector`, `error`, `null` — commented out as "Parsed manually" /
"Not used" because pyrogram's parser handles those itself) followed by an exact,
line-for-line mirror of tdesktop's api.tl body, starting at the `inputPeerEmpty`
constructor. Diffing the two confirms it: past that point, every line matches upstream
in order, all the way to EOF.

That means the body can be resynced mechanically without parsing TL syntax at all: find
the anchor line in both files and splice in the fresh upstream content from there on,
leaving the header untouched. Splicing today's upstream back in through this same anchor
reproduces the current file byte for byte, which is what makes this safe to run
unattended — the only way it could go wrong is upstream restructuring far enough that the
anchor line itself disappears, and that's handled below by refusing to touch the file.

Run standalone to try it locally: `python .github/scripts/sync_tl_schema.py`.
Set GITHUB_OUTPUT to also emit `changed`/`anchor_missing` for the workflow to branch on.
"""

from __future__ import annotations

import os
import pathlib
import sys
import urllib.request

UPSTREAM_URL = "https://raw.githubusercontent.com/telegramdesktop/tdesktop/dev/Telegram/SourceFiles/mtproto/scheme/api.tl"
# The first line after the hand-curated header where upstream and the curated file are
#  known to agree exactly.
ANCHOR = "inputPeerEmpty#7f3b18ea = InputPeer;\n"

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "compiler" / "api" / "source" / "main_api.tl"
SNAPSHOT_PATH = REPO_ROOT / "compiler" / "api" / "upstream_snapshot" / "api.tl"


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

    upstream_lines = upstream.splitlines(keepends=True)
    local_lines = SCHEMA_PATH.read_text(encoding="utf-8").splitlines(keepends=True)

    try:
        upstream_anchor = upstream_lines.index(ANCHOR)
        local_anchor = local_lines.index(ANCHOR)
    except ValueError:
        print(
            f"Anchor line not found ({ANCHOR!r}). Upstream's format (or the curated "
            "header) changed enough that the split point needs a human to re-derive. "
            "Leaving compiler/api/source/main_api.tl untouched.",
            file=sys.stderr,
        )
        _set_output("changed", "false")
        _set_output("anchor_missing", "true")
        return 0

    new_schema = "".join(local_lines[:local_anchor] + upstream_lines[upstream_anchor:])
    # `newline="\n"` pins the line ending: without it, `write_text` translates every `\n`
    #  to `os.linesep` on write, which turns every line into CRLF on Windows and disagrees
    #  with the LF the rest of the tree (and git) uses.
    SCHEMA_PATH.write_text(new_schema, encoding="utf-8", newline="\n")
    SNAPSHOT_PATH.write_text(upstream, encoding="utf-8", newline="\n")

    print("Synced compiler/api/source/main_api.tl from upstream tdesktop api.tl.")
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
