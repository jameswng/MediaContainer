"""
# ManagedSettings — Unit Tests for Settings module.

## Calling API
- `pytest tests/test_settings.py`: Execute tests for settings management, merging, and persistence.

## Algorithmic Methodology
- Verifies basic get/set functionality.
- Validates polymorphic input (dict vs Settings objects).
- Validates the `override` precedence logic (default: False).
- Verifies that `settings` overrides `path` content within the same call.
- Tests internal path updates when passing paths to methods.
- Ensures atomic disk persistence.

## Program Flow
1. Initialize `Settings` objects with various data/path/object combinations.
2. Test memory-to-disk and disk-to-memory synchronization.
3. Test merging of polymorphic sources with different override flags.
"""

import json
from managedsettings import Settings

class TestSettings:
    def test_basic_get_set(self):
        s = Settings()
        s.set("key", "value")
        assert s.get("key") == "value"
        assert s.get("nonexistent", "default") == "default"

    def test_persistence(self, tmp_path):
        config_file = tmp_path / "settings.json"
        s1 = Settings(config_file)
        
        s1.set("theme", "dark", save=True)
        assert config_file.exists()
        
        # Verify file content
        with config_file.open("r") as f:
            data = json.load(f)
            assert data["theme"] == "dark"
            
        # Load in a new instance
        s2 = Settings(config_file)
        assert s2.get("theme") == "dark"

    def test_path_updates(self, tmp_path):
        p1 = tmp_path / "one.json"
        p2 = tmp_path / "two.json"
        
        # Constructor path is always sticky
        s = Settings(p1)
        assert s.path == p1
        
        # save() without set_path should NOT update internal path
        s.save(p2, set_path=False)
        assert s.path == p1
        assert p2.exists()
        
        # merge() with set_path=True SHOULD update internal path
        s.merge(path=p2, set_path=True)
        assert s.path == p2

    def test_default_no_override(self):
        # 1. Start with existing data
        s = Settings(settings={"color": "red", "size": 10})
        
        # 2. Merge with override=False (the default)
        s.merge(settings={"color": "blue", "new_key": "exists"})
        assert s.get("color") == "red" # PRESERVED
        assert s.get("size") == 10
        assert s.get("new_key") == "exists"
        
        # 3. Explicit merge with override=True
        s.merge(settings={"color": "blue"}, override=True)
        assert s.get("color") == "blue" # REPLACED

    def test_argument_precedence(self, tmp_path):
        # The rule: settings overrides path file in the SAME call.
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"shared": "from_file", "file_only": "ok"}))
        
        s = Settings()
        # Even with override=False, the dict wins against the file in the internal merge.
        s.merge(path=config_file, settings={"shared": "from_dict"}, override=False)
        
        assert s.get("shared") == "from_dict"
        assert s.get("file_only") == "ok"

    def test_polymorphic_input(self):
        # 1. Source settings object
        s1 = Settings(settings={"a": 1, "b": 2})
        
        # 2. Initialize s2 using s1 as the source
        s2 = Settings(settings=s1)
        assert s2.get("a") == 1
        assert s2.get("b") == 2
        
        # 3. Merge from another object
        s3 = Settings(settings={"c": 3})
        s2.merge(settings=s3)
        assert s2.get("c") == 3

    def test_load_behavior(self):
        s = Settings(settings={"a": 1})
        # load() should clear memory
        s.load(settings={"b": 2})
        assert s.get("a") is None
        assert s.get("b") == 2

    def test_as_dict(self):
        s = Settings(settings={"a": 1, "b": 2})
        d = s.as_dict()
        assert d == {"a": 1, "b": 2}
        # Ensure it's a clone
        d["a"] = 99
        assert s.get("a") == 1

    def test_save_with_settings(self, tmp_path):
        config_file = tmp_path / "save_test.json"
        s = Settings(config_file)
        s.save(settings={"live": "data"})
        
        # Should be in memory (save overrides memory by design)
        assert s.get("live") == "data"
        # And on disk
        with config_file.open("r") as f:
            data = json.load(f)
            assert data["live"] == "data"
