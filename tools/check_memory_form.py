"""Signal-only check of the Layer 0 memory form (P20).

Runs as a PostToolUse hook on Write|Edit. It reads the hook payload from stdin,
checks only files under MEMORY_STORE, and exits 2 when a body declares
`Decided on:` without both `Premises:` and `Revisit if:`. Exit 2 sends stderr
to the model. It never edits or deletes a file (P7).
"""

import json
import os
import re
import sys

DECIDED = re.compile(r"(?m)^(\*\*)?Decided on:")
PREMISES = re.compile(r"(?m)^(\*\*)?Premises:")
REVISIT = re.compile(r"(?m)^(\*\*)?Revisit if:")


def main() -> int:
    store = os.environ.get("MEMORY_STORE")
    if not store:
        return 0

    payload = json.load(sys.stdin)
    path = payload.get("tool_input", {}).get("file_path", "")
    if not path or not os.path.abspath(path).startswith(os.path.abspath(store) + os.sep):
        return 0
    if not path.endswith(".md") or os.path.basename(path) == "MEMORY.md":
        return 0

    try:
        with open(path, encoding="utf-8") as handle:
            body = handle.read()
    except FileNotFoundError:
        return 0

    if not DECIDED.search(body):
        return 0

    missing = [
        name
        for name, pattern in (("Premises:", PREMISES), ("Revisit if:", REVISIT))
        if not pattern.search(body)
    ]
    if not missing:
        return 0

    print(
        f"{os.path.basename(path)} declares 'Decided on:' but lacks "
        f"{' and '.join(missing)} (design doc, Layer 0). Add the missing lines; "
        "the checker does not edit the file.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
