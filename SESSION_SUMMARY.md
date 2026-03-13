# Session Summary: DSL-Driven Parsing & Native Visual Analysis

## Full Session Recomposition
> **Full Session Recomposition**: `python3 bin/recompose_history.py`

## Current Truth
- **Architecture**: Transitions from hardcoded logic to a **Declarative Parser (DSL)** stored in `baked-in-rules.json`. Employs a hybrid configuration model (baked-in baseline + user overrides).
- **Visual Intelligence**: Implements macOS-native visual analysis using `sips`. Uses **Average Hash (aHash)** for structural matching (resizing/compression) and **Color Histograms** for pictorial similarity (crops/sets).
- **Core Principles**: Zero-external-dependency Computer Vision. All image processing is handled via standard system binaries.
- **Data Model**:
    - `ClassifiedFile`: Stores both normalized `stem` and unmodified `raw_stem`.
    - `MediaContainer`: Features a "Maximal Readable Name" algorithm and uses LCP of primary media for naming.
- **CLI Enhancements**: Supports multiple verbosity levels (`-v`, `-vv`). Implements concise gallery summarization (`gallery: [ 'stem##.type' ]`) to maintain high-signal output.
- **Verification**: ✅ 184/184 tests passing.

## Latest Session (Summary)
- **DSL Refactor**:
    - Extracted all parsing rules into `baked-in-rules.json`.
    - Implemented `Parser` class to handle iterative suffix peeling and mid-string sequence heuristics.
    - Added support for `parser_rules` in `~/.mediacontainer.json` for user customization.
- **Computer Vision Integration**:
    - Created `visual.py` utilizing `sips` for 8x8 aHash and 125-bin RGB histograms.
    - Implemented Hamming distance and Cosine similarity for automated regrouping of "weak" containers (e.g., `1.jpg`, `2.jpg`).
- **Naming Engine**:
    - Implemented dominant separator detection (preserves user style: `.`, `_`, or `-`).
    - Added metadata stripping (brackets/parentheses removal from container names).
- **Validation Suite**:
    - Added multiple directory fixtures for complex naming and visual scenarios.
    - Integrated standard benchmark images (`lena`, `baboon`, `cameraman`) into the test suite.
    - Verified 184 tests passing across all naming, grouping, and visual modules.
