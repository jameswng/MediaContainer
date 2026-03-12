#!/usr/bin/env python3
"""
Session Recomposition Tool
Reconstructs the context and architectural truth for the next agent.
"""

import sys
from pathlib import Path

def main():
    root = Path(__file__).parent.parent
    summary = root / "SESSION_SUMMARY.md"
    arch = root / "ARCHITECTURE.md"

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
    import subprocess
    try:
        res = subprocess.run(["git", "log", "-n", "5", "--oneline"], capture_output=True, text=True)
        print(res.stdout)
    except Exception:
        print("Git log unavailable.")

if __name__ == "__main__":
    main()
