"""
# MediaContainer — Unit Tests for Visual Analysis.
"""

import os
from pathlib import Path
import pytest
from mediacontainer.visual import VisualFingerprint

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "visual_test"

@pytest.mark.skipif(os.uname().sysname != "Darwin", reason="sips is macOS only")
class TestVisual:

    def test_fingerprint_generation(self):
        img_path = FIXTURE_DIR / "cameraman.png"
        if not img_path.exists():
            pytest.skip(f"Test image {img_path} not found")

        fp = VisualFingerprint.get_fingerprint(img_path)
        assert fp is not None
        assert len(fp) == 64
        assert all(c in "01" for c in fp)

    def test_hamming_distance(self):
        h1 = "1" * 64
        h2 = ("1" * 63) + "0"
        assert VisualFingerprint.calculate_distance(h1, h2) == 1
        assert VisualFingerprint.calculate_distance(h1, h1) == 0
        
    def test_visual_similarity(self):
        img1 = FIXTURE_DIR / "cameraman.png"
        img2 = FIXTURE_DIR / "cameraman_128.png"
        
        if not img1.exists() or not img2.exists():
            pytest.skip("Test images not found")
            
        fp1 = VisualFingerprint.get_fingerprint(img1)
        fp2 = VisualFingerprint.get_fingerprint(img2)
        
        distance = VisualFingerprint.calculate_distance(fp1, fp2)
        # Resizing should result in very low Hamming distance
        assert distance <= 5

    def test_visual_distinctness(self):
        img1 = FIXTURE_DIR / "cameraman.png"
        img2 = FIXTURE_DIR / "baboon.jpg"
        
        if not img1.exists() or not img2.exists():
            pytest.skip("Test images not found")
            
        fp1 = VisualFingerprint.get_fingerprint(img1)
        fp2 = VisualFingerprint.get_fingerprint(img2)
        
        distance = VisualFingerprint.calculate_distance(fp1, fp2)
        # Distinct images should have high Hamming distance
        assert distance > 15

    def test_histogram_correlation(self):
        d = Path("tests/fixtures/lena_variants")
        img1 = d / "original.jpg"
        img2 = d / "tiny.png"
        img3 = d / "grayscale.jpg"
        
        if not all(p.exists() for p in [img1, img2, img3]):
            pytest.skip("Lena variants not found")
            
        h1 = VisualFingerprint.get_histogram(img1)
        h2 = VisualFingerprint.get_histogram(img2)
        h3 = VisualFingerprint.get_histogram(img3)
        
        assert VisualFingerprint.calculate_histogram_correlation(h1, h2) > 0.95
        # Grayscale should have low correlation with color original
        assert VisualFingerprint.calculate_histogram_correlation(h1, h3) < 0.5
