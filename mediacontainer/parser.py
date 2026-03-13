"""
# MediaContainer — Filename Parser module.

## Calling API
- `Parser(settings: SettingsProtocol | None = None)`: Initialize the parser.
- `Parser.parse(path: Path) -> ParseResult`: Decompose a filename using rules.

## Algorithmic Methodology
- **Rule-based Decomposition**: Uses a set of declarative rules loaded from 
  `baked-in-rules.json` and optional user overrides.
- **Suffix Peeling**: Iteratively removes matching patterns from the right.
- **Global Extraction**: Applies rules anywhere in the filename (e.g., mid-string).
- **Function Placeholders**: Complex heuristics are implemented as methods and
  triggered via rule configuration.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SettingsProtocol(Protocol):
    path: Path | None
    def get(self, key: str, default: Any = None) -> Any: ...


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: str | None = None
    function: str | None = None
    action: str = "peel"  # peel, strip
    scope: str = "suffix" # suffix, global
    
    @property
    def regex(self) -> re.Pattern | None:
        if self.pattern:
            return re.compile(self.pattern, re.IGNORECASE)
        return None


@dataclass
class ParseResult:
    stem: str
    raw_stem: str
    extension: str = ""
    volume: str | None = None
    split: str | None = None
    sequence: str | None = None
    qualifier: str | None = None
    is_gallery_seq: bool = False


class Parser:
    """Handles filename decomposition using declarative rules."""

    def __init__(self, settings: SettingsProtocol | None = None):
        self.rules = self._load_baked_in_rules()
        if settings:
            custom_rules = settings.get("parser_rules", [])
            for r_dict in custom_rules:
                if "scope" not in r_dict:
                    r_dict["scope"] = "global"
                self.rules.insert(0, Rule(**r_dict))

    def _load_baked_in_rules(self) -> list[Rule]:
        rules_path = Path(__file__).parent / "baked-in-rules.json"
        if not rules_path.exists():
            return []
        try:
            data = json.loads(rules_path.read_text())
            return [Rule(**r) for r in data]
        except Exception:
            return []

    def parse(self, path: Path) -> ParseResult:
        filename = path.name
        peeled_name = filename
        
        res = ParseResult(stem="", raw_stem="")

        # 1. Iterative Suffix Peeling Loop
        while True:
            changed = False
            for rule in self.rules:
                if rule.scope != "suffix" or not rule.regex:
                    continue
                
                m = rule.regex.search(peeled_name)
                if m:
                    val = m.group()
                    if rule.action == "peel":
                        if rule.name == "split" and not res.split:
                            res.split = val
                        elif rule.name.startswith("volume") and not res.volume:
                            res.volume = val
                        elif rule.name == "extension" and not res.extension:
                            res.extension = val
                        
                        peeled_name = peeled_name[:-len(val)]
                        changed = True
                        break
                    elif rule.action == "strip":
                        if rule.name == "qualifier":
                            res.qualifier = val.lstrip("-._")
                        peeled_name = peeled_name[:-len(val)]
                        changed = True
                        break
            if not changed:
                break

        # 2. Global and Function Rule Application
        for rule in self.rules:
            if rule.scope == "suffix":
                continue
            
            if rule.function:
                method = getattr(self, rule.function, None)
                if method:
                    peeled_name = method(res, peeled_name)
                continue

            if rule.regex:
                m = rule.regex.search(peeled_name)
                if m:
                    val = m.group()
                    if rule.action == "peel":
                        if rule.name == "sequence" and not res.sequence:
                            res.sequence = m.group(1) if m.groups() else val
                        peeled_name = peeled_name[:m.start()] + " " + peeled_name[m.end():]
                    elif rule.action == "strip":
                        peeled_name = peeled_name[:m.start()] + " " + peeled_name[m.end():]

        # 3. Finalization
        res.raw_stem = peeled_name
        
        # Normalize stem for grouping
        normalized = peeled_name.lower()
        normalized = re.sub(r"[._()\[\]]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        res.stem = normalized

        return res

    def _heuristic_sequence_extraction(self, res: ParseResult, peeled_name: str) -> str:
        """Complex heuristic for image galleries and mid-string sequences."""
        from .media_container import IMAGE_EXTS, ACCESSORY_NAMES
        
        if res.extension.lower() in IMAGE_EXTS or (res.split and res.extension == ""):
            # Matches: optional separator, digits, separator or end
            seq_regex = re.compile(r"([-_.[(\]]?)(\d+)([-_.)\]]?)")
            matches = list(seq_regex.finditer(peeled_name))
            
            if matches:
                # To avoid misidentifying years/resolutions, we use RE_RESOLUTION/RE_YEAR
                # defined in media_container or locally.
                RE_RESOLUTION = re.compile(r"^(?:720|1080|2160|480|576)[pi]?$", re.IGNORECASE)
                RE_YEAR = re.compile(r"^(?:19|20)\d{2}$")

                for m in reversed(matches):
                    found_seq = m.group(2)
                    if RE_RESOLUTION.match(found_seq) or RE_YEAR.match(found_seq):
                        continue
                        
                    has_sep = bool(m.group(1)) or bool(m.group(3))
                    prefix = peeled_name[:m.start()].lower().strip("-_.")
                    
                    if len(found_seq) >= 2 or has_sep or prefix in ACCESSORY_NAMES:
                        res.sequence = found_seq
                        res.is_gallery_seq = True
                        return peeled_name[:m.start()] + " " + peeled_name[m.end():]
        return peeled_name
