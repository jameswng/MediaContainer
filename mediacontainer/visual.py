"""
# MediaContainer — Visual Analysis module.

## Calling API
- `VisualFingerprint.get_fingerprint(path: Path) -> str`: Structural hash (aHash).
- `VisualFingerprint.get_histogram(path: Path) -> list[float]`: Normalized color distribution.
- `VisualFingerprint.calculate_distance(h1: str, h2: str) -> int`: Structural distance.
- `VisualFingerprint.calculate_histogram_correlation(hist1: list[float], hist2: list[float]) -> float`: 
  Similarity score (0.0 to 1.0).

## Algorithmic Methodology
- **macOS Native Analysis**: Uses `sips` for image processing.
- **Average Hash (aHash)**: Downsample to 8x8, grayscale, threshold by average.
- **Color Histogram**: 
    1. Downsample to 32x32.
    2. Quantize into 125 bins (5 per channel R, G, B).
    3. Calculate frequency and normalize by total pixels.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path


class VisualFingerprint:
    """Utility for generating visual fingerprints and histograms using macOS sips."""

    @staticmethod
    def get_fingerprint(path: Path, resolution: int = 8) -> str | None:
        """Generate a structural hash (aHash) for an image."""
        if os.uname().sysname != "Darwin":
            return None

        with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            cmd = ["sips", "-s", "format", "bmp", "-z", str(resolution), str(resolution), str(path), "--out", str(tmp_path)]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            data = tmp_path.read_bytes()
            # BMP Header is 54 bytes. Pixels are 3 bytes each (RGB).
            expected_pixels = resolution * resolution
            if len(data) < 54 + (expected_pixels * 3):
                return None

            pixels = []
            for i in range(54, 54 + (expected_pixels * 3), 3):
                b, g, r = data[i], data[i+1], data[i+2]
                gray = (r + g + b) // 3
                pixels.append(gray)

            avg = sum(pixels) / len(pixels)
            return "".join(["1" if p > avg else "0" for p in pixels])
        except Exception:
            return None
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    @staticmethod
    def get_histogram(path: Path) -> list[float] | None:
        """Generate a normalized 125-bin color histogram (RGB quantized to 5 levels per channel)."""
        if os.uname().sysname != "Darwin":
            return None

        with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            cmd = ["sips", "-s", "format", "bmp", "-z", "32", "32", str(path), "--out", str(tmp_path)]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            data = tmp_path.read_bytes()
            if len(data) < 54 + (32 * 32 * 3):
                return None

            # 125 bins: 5*5*5
            hist = [0] * 125
            total_pixels = 32 * 32
            
            for i in range(54, 54 + (32 * 32 * 3), 3):
                b, g, r = data[i], data[i+1], data[i+2]
                
                # Quantize each channel 0-255 -> 0-4
                rq = min(r // 52, 4)
                gq = min(g // 52, 4)
                bq = min(b // 52, 4)
                
                idx = (rq * 25) + (gq * 5) + bq
                hist[idx] += 1
                
            return [v / total_pixels for v in hist]
        except Exception:
            return None
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    @staticmethod
    def calculate_distance(h1: str, h2: str) -> int:
        """Compute Hamming distance between two binary strings."""
        if not h1 or not h2 or len(h1) != len(h2):
            return 999
        return sum(c1 != c2 for c1, c2 in zip(h1, h2))

    @staticmethod
    def calculate_histogram_correlation(hist1: list[float], hist2: list[float]) -> float:
        """Compute cosine similarity between two normalized histograms."""
        if not hist1 or not hist2 or len(hist1) != len(hist2):
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(hist1, hist2))
        magnitude1 = sum(a * a for a in hist1) ** 0.5
        magnitude2 = sum(b * b for b in hist2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        return dot_product / (magnitude1 * magnitude2)
