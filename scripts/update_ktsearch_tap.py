#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path


def main() -> int:
    script = Path(__file__).with_name("update_formulae.py")
    args = [
        sys.executable,
        str(script),
        "--formula",
        "ktsearch",
        *sys.argv[1:],
    ]
    return subprocess.call(args)


if __name__ == "__main__":
    raise SystemExit(main())
