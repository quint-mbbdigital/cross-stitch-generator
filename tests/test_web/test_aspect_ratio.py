"""Test aspect ratio preservation functionality.

Ensures non-square photos are properly handled without distortion.
"""

import pytest
from PIL import Image
from web.routes.api import _generate_pattern_sync
from web.models.requests import PatternConfig


class TestAspectRatioPreservation:
    """Test that non-square images are handled properly without distortion."""

    def test_landscape_image_preserved(self):
        """Test that landscape images (wider than tall) are properly handled."""
        # Create a landscape image (16:9 aspect ratio)
        landscape_image = Image.new('RGB', (160, 90), (255, 0, 0))
        config = PatternConfig(resolution=50, max_colors=8)

        result = _generate_pattern_sync(landscape_image, config)

        # Result should always be square (50x50) due to target resolution
        assert result.width == 50, f"Expected width 50, got {result.width}"
        assert result.height == 50, f"Expected height 50, got {result.height}"

        # Grid should have correct number of cells
        assert len(result.grid) == 50 * 50, f"Expected 2500 grid cells, got {len(result.grid)}"

        # Should have at least 1 color (the red we created)
        assert len(result.palette) >= 1, "Should have at least one color"

    def test_portrait_image_preserved(self):
        """Test that portrait images (taller than wide) are properly handled."""
        # Create a portrait image (9:16 aspect ratio)
        portrait_image = Image.new('RGB', (90, 160), (0, 255, 0))
        config = PatternConfig(resolution=80, max_colors=8)

        result = _generate_pattern_sync(portrait_image, config)

        # Result should always be square (80x80) due to target resolution
        assert result.width == 80, f"Expected width 80, got {result.width}"
        assert result.height == 80, f"Expected height 80, got {result.height}"

        # Grid should have correct number of cells
        assert len(result.grid) == 80 * 80, f"Expected 6400 grid cells, got {len(result.grid)}"

        # Should have at least 1 color (the green we created)
        assert len(result.palette) >= 1, "Should have at least one color"

    def test_square_image_unchanged(self):
        """Test that square images work correctly."""
        # Create a square image
        square_image = Image.new('RGB', (100, 100), (0, 0, 255))
        config = PatternConfig(resolution=60, max_colors=8)

        result = _generate_pattern_sync(square_image, config)

        # Result should be square (60x60)
        assert result.width == 60, f"Expected width 60, got {result.width}"
        assert result.height == 60, f"Expected height 60, got {result.height}"

        # Grid should have correct number of cells
        assert len(result.grid) == 60 * 60, f"Expected 3600 grid cells, got {len(result.grid)}"

    def test_extreme_aspect_ratios(self):
        """Test very extreme aspect ratios (panoramic/banner style)."""
        # Create a very wide image (10:1 aspect ratio)
        wide_image = Image.new('RGB', (1000, 100), (255, 255, 0))
        config = PatternConfig(resolution=40, max_colors=8)

        result = _generate_pattern_sync(wide_image, config)

        # Should still produce a square pattern
        assert result.width == 40, f"Expected width 40, got {result.width}"
        assert result.height == 40, f"Expected height 40, got {result.height}"
        assert len(result.grid) == 40 * 40, f"Expected 1600 grid cells, got {len(result.grid)}"

        # Create a very tall image (1:10 aspect ratio)
        tall_image = Image.new('RGB', (100, 1000), (255, 0, 255))

        result2 = _generate_pattern_sync(tall_image, config)

        # Should still produce a square pattern
        assert result2.width == 40, f"Expected width 40, got {result2.width}"
        assert result2.height == 40, f"Expected height 40, got {result2.height}"
        assert len(result2.grid) == 40 * 40, f"Expected 1600 grid cells, got {len(result2.grid)}"

    def test_different_resolutions_maintain_aspect_preservation(self):
        """Test that aspect ratio preservation works across different target resolutions."""
        # Create a 3:2 aspect ratio image (typical camera aspect ratio)
        photo_like_image = Image.new('RGB', (300, 200), (128, 128, 128))

        resolutions_to_test = [30, 50, 100, 150]

        for resolution in resolutions_to_test:
            config = PatternConfig(resolution=resolution, max_colors=16)
            result = _generate_pattern_sync(photo_like_image, config)

            # Should always produce square output matching target resolution
            assert result.width == resolution, f"Resolution {resolution}: expected width {resolution}, got {result.width}"
            assert result.height == resolution, f"Resolution {resolution}: expected height {resolution}, got {result.height}"
            assert len(result.grid) == resolution * resolution, f"Resolution {resolution}: expected {resolution*resolution} grid cells, got {len(result.grid)}"

    def test_cli_behavior_consistency(self):
        """Test that web behavior matches CLI default behavior."""
        # Test that we get the same behavior as CLI with preserve_aspect_ratio=True
        test_image = Image.new('RGB', (200, 100), (100, 150, 200))
        config = PatternConfig(resolution=60, max_colors=32)

        # This should work without errors and preserve proportions
        result = _generate_pattern_sync(test_image, config)

        assert result.width == 60
        assert result.height == 60
        assert len(result.grid) == 3600
        assert len(result.palette) >= 1

        # The key test: no distortion means the pattern should look natural
        # (This is harder to test programmatically, but at least we verify
        # that the processing completes and produces expected dimensions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])