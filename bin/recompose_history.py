#!/usr/bin/env python3
"""
# MediaContainer — Session Recomposition Tool

## Calling API
- `bin/recompose_history.py [-h | --help]`: Execute the tool to display session summary
  and architectural context.

## Algorithmic Methodology
- **Path Resolution**: Programmatically determines the project root relative to the
  script's location.
- **Environment Injection**: Injects the project root into `sys.path` to ensure
  module discoverability.
- **Context Gathering**: Reads `SESSION_SUMMARY.md`, `ARCHITECTURE.md`, and git history.
- **Environment-Clean Safe**: Ensures subprocesses run with a restricted PATH and
  clean environment via `env -i`.

## Program Flow
1. Resolve the script's physical location and the project root.
2. Inject the root directory into `sys.path`.
3. Handle `--help` if requested.
4. Locate and display `SESSION_SUMMARY.md` if available.
5. Locate and display the first 20 lines of `ARCHITECTURE.md`.
6. Display the most recent 5 git commit messages using a clean environment.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# --- Constants ---
STRICT_PATH = "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/opt/homebrew/sbin"

# --- Self-Locating Executable ---
# Resolve absolute physical path and inject project root into environment
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(
        prog="recompose_history",
        description="Reconstructs the context and architectural truth for the next agent.",
    )
    parser.parse_args()

    summary = ROOT / "SESSION_SUMMARY.md"
    arch = ROOT / "ARCHITECTURE.md"

    print("=== Session Recomposition System ===")
    
    if summary.exists():
        print(f"\n[SUMMARY] Loading {summary.name}...")
        print(summary.read_text())
    else:
        print("\n[ERROR] SESSION_SUMMARY.md not found.")

    if arch.exists():
        print(f"\n[ARCHITECTURE] Loading {arch.name}...")
        # Print just the top part to avoid too much noise
        content = arch.read_text().splitlines()
        print("\n".join(content[:20]))
        print("...")
    else:
        print("\n[ERROR] ARCHITECTURE.md not found.")

    print("\n[GIT] Recent Checkpoints:")
    
    # Environment-Clean Safe execution of Git
    clean_env = {
        "HOME": os.environ.get("HOME", ""),
        "USER": os.environ.get("USER", ""),
        "PATH": STRICT_PATH,
        "TERM": os.environ.get("TERM", "xterm-256color")
    }
    
    try:
        res = subprocess.run(
            ["git", "log", "-n", "5", "--oneline"],
            capture_output=True,
            text=True,
            check=False,
            env=clean_env
        )
        print(res.stdout)
    except Exception:
        print("Git log unavailable.")

if __name__ == "__main__":
    main()
