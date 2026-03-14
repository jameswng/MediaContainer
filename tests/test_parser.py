"""
# MediaContainer — Unit Tests for Filename Parser.
"""

from pathlib import Path
from mediacontainer.parser import Parser

class TestParser:

    def test_default_rules_loading(self):
        parser = Parser()
        assert len(parser.rules) >= 6
        assert any(r.name == "split" for r in parser.rules)

    def test_basic_peeling(self):
        parser = Parser()
        res = parser.parse(Path("movie.mkv"))
        assert res.extension == ".mkv"
        assert res.stem == "movie"

    def test_complex_peeling(self):
        parser = Parser()
        res = parser.parse(Path("release.part1.rar.001"))
        assert res.split == ".001"
        assert res.extension == ".rar"
        assert res.volume == ".part1"
        assert res.stem == "release"

    def test_heuristic_sequence(self):
        parser = Parser()
        # Heuristic triggers for images
        res = parser.parse(Path("Holiday_01_Paris.jpg"))
        assert res.sequence == "01"
        assert res.is_gallery_seq is True
        assert res.stem == "holiday paris"

    def test_custom_rules(self):
        class MockSettings:
            path = None
            def get(self, key, default=None):
                if key == "parser_rules":
                    return [{"name": "tag", "pattern": r"\[TAG\]", "action": "strip"}]
                return default
        
        parser = Parser(MockSettings())
        res = parser.parse(Path("movie [TAG].mkv"))
        assert res.stem == "movie"
