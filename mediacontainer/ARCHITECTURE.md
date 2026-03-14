# MediaContainer Architecture

## Purpose
Scan a directory, identify which files belong together as logical "media containers," extract any archives, and play the resulting media.

## Core Problem
Files in a directory may form one or more **media containers**. Files are related by naming convention, but the conventions vary. Usually there is one media container per directory, but not always.

---

## MediaContainer Module
**Standalone library module, decoupled from extraction and playback. Importable by other apps.**

### Interface
```python
class MediaContainer:
    name: str
    stem: str
    lcp: str  # alias to stem
    files: list[ClassifiedFile]

    @classmethod
    def from_paths(cls, paths: list[Path]) -> list[MediaContainer]:
        """Accept a list of Paths, classify and group them,
        return one or more MediaContainer instances."""
```

- Initial classification and grouping uses filenames only (pure string logic).
- **Visual Analysis Fallback**: for cases where filename heuristics are insufficient, performs macOS native visual fingerprinting to identify logical sets.

---

## Design Mandates (Inherited from Root)

### 1. Modern Technical Excellence
- **Python 3.11+**, **Strict Type Annotation**, `pathlib`, `ruff`.
- **Environment-Clean Safe**: Scripts MUST use `#!/usr/bin/env python3` and an internal `os.environ` pruning block.

### 5. Self-Documenting Source Headers
Every source file MUST begin with a header detailing Calling API, Algorithmic Methodology, and Program Flow.

---

## Filename Anatomy
A filename is decomposed into named parts during classification:
`stem-sample.part1.rar.001`
- **stem**: the normalized core name (lowercase, space-separated)
- **qualifier**: descriptive suffix (sample, screenshot, subs)
- **volume**: multipart/volume indicator (.part1, .r00, .vol0+1)
- **extension**: file type extension (.rar)
- **split**: numeric split suffix (.001)

---

## Stem Extraction (Rule-based Parser DSL)
Stems are identified by a declarative `Parser` that applies ordered rules from `baked-in-rules.json`.
- **Peel**: Extracts a value and removes it.
- **Strip**: Removes recognized tokens.
- **Scopes**: Suffix (right-to-left) or Global.

---

## Grouping & Visual Analysis
1. **LCP Clustering**: Cluster files by normalized stems.
2. **Visual Clustering (macOS)**: Verification tool for "weak" (numeric/empty) or "inconsistent" groups.
    - **Structural Match**: Average Hash (Hamming distance ≤ 10).
    - **Pictorial Match**: Color Histogram (Cosine similarity ≥ 0.95).
3. **Accessory Attachment**: Generic accessories (front.jpg) attach to the dominant group.

---

## Container Naming (Maximal Readable Name)
Derived from the unmodified Longest Common Prefix (LCP) of the grouped files' `raw_stem` attributes.
1. Extract LCP.
2. Identify dominant separator.
3. Cleanup and normalize.

---

## CLI Display (Gallery Summarization)
Summarizes sequential image sets by default (`stem##.type`).
- `-v`: Displays pattern.
- `-vv`: Displays full list.
