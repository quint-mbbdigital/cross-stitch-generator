"""Color management and quantization for cross-stitch patterns."""

from typing import List, Tuple
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

from ..models import Color, ColorPalette, GeneratorConfig
from ..utils import ColorQuantizationError


class ColorManager:
    """Manages color quantization and palette creation for cross-stitch patterns."""

    def __init__(self, config: GeneratorConfig):
        """
        Initialize ColorManager with configuration.

        Args:
            config: Generator configuration object
        """
        self.config = config

    def quantize_image(self, image: Image.Image) -> Tuple[ColorPalette, np.ndarray]:
        """
        Quantize image colors and return palette and color indices.

        Args:
            image: PIL Image object

        Returns:
            Tuple of (ColorPalette, color_indices_array)

        Raises:
            ColorQuantizationError: If quantization fails
        """
        try:
            # Convert image to numpy array
            if image.mode != 'RGB':
                image = image.convert('RGB')

            image_array = np.array(image)
            height, width = image_array.shape[:2]

            # Reshape to list of pixels
            pixels = image_array.reshape(-1, 3)

            # Choose quantization method
            if self.config.quantization_method == "median_cut":
                palette_colors = self._median_cut_quantization(pixels)
            elif self.config.quantization_method == "kmeans":
                palette_colors = self._kmeans_quantization(pixels)
            else:
                raise ColorQuantizationError(
                    f"Unknown quantization method: {self.config.quantization_method}",
                    method=self.config.quantization_method
                )

            # Create ColorPalette object
            color_objects = [
                Color(r=int(rgb[0]), g=int(rgb[1]), b=int(rgb[2]))
                for rgb in palette_colors
            ]
            palette = ColorPalette(
                colors=color_objects,
                max_colors=self.config.max_colors,
                quantization_method=self.config.quantization_method
            )

            # Map each pixel to closest palette color
            color_indices = self._map_pixels_to_palette(pixels, palette_colors)
            color_indices = color_indices.reshape(height, width)

            return palette, color_indices

        except Exception as e:
            if isinstance(e, ColorQuantizationError):
                raise
            raise ColorQuantizationError(
                f"Color quantization failed: {e}",
                method=self.config.quantization_method,
                max_colors=self.config.max_colors,
                cause=e
            )

    def _median_cut_quantization(self, pixels: np.ndarray) -> List[Tuple[int, int, int]]:
        """
        Perform median cut quantization.

        Args:
            pixels: Array of RGB pixels (n_pixels, 3)

        Returns:
            List of RGB tuples representing the quantized palette
        """
        try:
            # Remove duplicate pixels to speed up processing
            unique_pixels, inverse_indices = np.unique(pixels, axis=0, return_inverse=True)

            # Count occurrences of each unique pixel
            pixel_counts = np.bincount(inverse_indices)

            # Create initial box containing all pixels
            initial_box = ColorBox(unique_pixels, pixel_counts)
            boxes = [initial_box]

            # Split boxes until we have desired number of colors
            target_colors = min(self.config.max_colors, len(unique_pixels))

            while len(boxes) < target_colors:
                # Find box with largest volume to split
                largest_box = max(boxes, key=lambda box: box.volume())

                if largest_box.volume() == 0:
                    # No more boxes can be split
                    break

                # Split the box
                box1, box2 = largest_box.split()
                boxes.remove(largest_box)
                boxes.extend([box1, box2])

            # Get representative color for each box
            palette_colors = []
            for box in boxes:
                color = box.get_average_color()
                palette_colors.append((int(color[0]), int(color[1]), int(color[2])))

            return palette_colors

        except Exception as e:
            raise ColorQuantizationError(
                f"Median cut quantization failed: {e}",
                method="median_cut",
                cause=e
            )

    def _kmeans_quantization(self, pixels: np.ndarray) -> List[Tuple[int, int, int]]:
        """
        Perform K-means quantization.

        Args:
            pixels: Array of RGB pixels (n_pixels, 3)

        Returns:
            List of RGB tuples representing the quantized palette
        """
        try:
            # Determine number of clusters
            unique_pixels = np.unique(pixels, axis=0)
            n_colors = min(self.config.max_colors, len(unique_pixels))

            if n_colors == 1:
                # Only one unique color
                color = unique_pixels[0]
                return [(int(color[0]), int(color[1]), int(color[2]))]

            # Perform K-means clustering
            # Use n_jobs=1 to avoid threading issues on macOS with OpenBLAS
            kmeans = KMeans(
                n_clusters=n_colors,
                random_state=42,
                n_init=10,
                max_iter=300,
                n_jobs=1
            )

            # Use a sample of pixels if there are too many
            max_samples = 10000
            if len(pixels) > max_samples:
                sample_indices = np.random.choice(len(pixels), max_samples, replace=False)
                sample_pixels = pixels[sample_indices]
            else:
                sample_pixels = pixels

            kmeans.fit(sample_pixels)

            # Get cluster centers as palette colors
            palette_colors = []
            for center in kmeans.cluster_centers_:
                # Ensure values are in valid range and convert to int
                center = np.clip(center, 0, 255)
                palette_colors.append((int(center[0]), int(center[1]), int(center[2])))

            return palette_colors

        except Exception as e:
            # If K-means fails (often due to threading issues), fall back to median cut
            try:
                import logging
                logging.warning(f"K-means quantization failed ({e}), falling back to median cut")
                return self._median_cut_quantization(pixels)
            except Exception as fallback_error:
                raise ColorQuantizationError(
                    f"K-means quantization failed: {e}, median cut fallback also failed: {fallback_error}",
                    method="kmeans",
                    cause=e
                )

    def _map_pixels_to_palette(self, pixels: np.ndarray,
                               palette_colors: List[Tuple[int, int, int]]) -> np.ndarray:
        """
        Map each pixel to the closest color in the palette.

        Args:
            pixels: Array of RGB pixels (n_pixels, 3)
            palette_colors: List of palette RGB tuples

        Returns:
            Array of color indices
        """
        # Convert palette to numpy array for efficient computation
        palette_array = np.array(palette_colors)

        # Calculate squared Euclidean distances between each pixel and each palette color
        # Using broadcasting: (n_pixels, 1, 3) - (1, n_colors, 3) = (n_pixels, n_colors, 3)
        distances = np.sum((pixels[:, np.newaxis, :] - palette_array[np.newaxis, :, :]) ** 2, axis=2)

        # Find closest palette color for each pixel
        color_indices = np.argmin(distances, axis=1)

        return color_indices

    def optimize_palette_for_excel(self, palette: ColorPalette) -> ColorPalette:
        """
        Optimize color palette for Excel compatibility.

        Args:
            palette: Original color palette

        Returns:
            Optimized color palette
        """
        # Excel can handle millions of colors, but for practical purposes,
        # we might want to ensure good contrast and distinctness

        optimized_colors = []

        for color in palette.colors:
            # Ensure colors are distinct and have good contrast
            optimized_color = self._ensure_color_distinctness(color, optimized_colors)
            optimized_colors.append(optimized_color)

        return ColorPalette(
            colors=optimized_colors,
            max_colors=palette.max_colors,
            quantization_method=palette.quantization_method
        )

    def _ensure_color_distinctness(self, new_color: Color,
                                   existing_colors: List[Color],
                                   min_distance: float = 30.0) -> Color:
        """
        Ensure a color is distinct from existing colors.

        Args:
            new_color: Color to check
            existing_colors: List of existing colors
            min_distance: Minimum Euclidean distance required

        Returns:
            Adjusted color that maintains minimum distance
        """
        if not existing_colors:
            return new_color

        # Check if color is distinct enough
        for existing_color in existing_colors:
            if new_color.distance_to(existing_color) < min_distance:
                # Adjust color to maintain distance
                return self._adjust_color_for_distance(new_color, existing_colors, min_distance)

        return new_color

    def _adjust_color_for_distance(self, color: Color, existing_colors: List[Color],
                                   min_distance: float) -> Color:
        """
        Adjust color to maintain minimum distance from existing colors.

        Args:
            color: Original color
            existing_colors: List of existing colors
            min_distance: Minimum required distance

        Returns:
            Adjusted color
        """
        # Simple adjustment: modify brightness if colors are too close
        adjusted_r = min(255, max(0, color.r + 20))
        adjusted_g = min(255, max(0, color.g + 20))
        adjusted_b = min(255, max(0, color.b + 20))

        adjusted_color = Color(r=adjusted_r, g=adjusted_g, b=adjusted_b)

        # Check if adjustment helped
        min_existing_distance = min(
            adjusted_color.distance_to(existing) for existing in existing_colors
        )

        if min_existing_distance >= min_distance:
            return adjusted_color
        else:
            # If adjustment didn't help enough, return original color
            return color

    def get_color_statistics(self, image: Image.Image,
                             palette: ColorPalette,
                             color_indices: np.ndarray) -> dict:
        """
        Get statistics about color usage in the quantized image.

        Args:
            image: Original image
            palette: Color palette
            color_indices: Array of color indices

        Returns:
            Dictionary with color statistics
        """
        # Count usage of each color
        unique_indices, counts = np.unique(color_indices, return_counts=True)
        total_pixels = color_indices.size

        color_stats = {
            'total_pixels': total_pixels,
            'unique_colors_in_palette': len(palette),
            'colors_actually_used': len(unique_indices),
            'color_usage': {}
        }

        for idx, count in zip(unique_indices, counts):
            color = palette[idx]
            percentage = (count / total_pixels) * 100
            color_stats['color_usage'][idx] = {
                'color': color.hex_code,
                'count': int(count),
                'percentage': round(percentage, 2)
            }

        return color_stats


class ColorBox:
    """Represents a box of colors for median cut quantization."""

    def __init__(self, pixels: np.ndarray, counts: np.ndarray):
        """
        Initialize ColorBox.

        Args:
            pixels: Array of RGB pixels in this box
            counts: Count of each pixel
        """
        self.pixels = pixels
        self.counts = counts

    def volume(self) -> int:
        """Calculate volume (product of RGB ranges)."""
        if len(self.pixels) == 0:
            return 0

        ranges = np.ptp(self.pixels, axis=0)  # peak-to-peak (max - min) for each channel
        return int(np.prod(ranges))

    def split(self) -> Tuple['ColorBox', 'ColorBox']:
        """
        Split box along the longest dimension.

        Returns:
            Tuple of two ColorBox objects
        """
        if len(self.pixels) <= 1:
            # Cannot split further
            return self, ColorBox(np.array([]).reshape(0, 3), np.array([]))

        # Find dimension with largest range
        ranges = np.ptp(self.pixels, axis=0)
        split_dim = np.argmax(ranges)

        # Sort by the chosen dimension
        sorted_indices = np.argsort(self.pixels[:, split_dim])
        sorted_pixels = self.pixels[sorted_indices]
        sorted_counts = self.counts[sorted_indices]

        # Find median based on pixel counts (weighted median)
        cumulative_counts = np.cumsum(sorted_counts)
        total_count = cumulative_counts[-1]
        median_index = np.searchsorted(cumulative_counts, total_count // 2)

        # Ensure we don't create empty boxes
        median_index = max(1, min(median_index, len(sorted_pixels) - 1))

        # Split into two boxes
        box1_pixels = sorted_pixels[:median_index]
        box1_counts = sorted_counts[:median_index]

        box2_pixels = sorted_pixels[median_index:]
        box2_counts = sorted_counts[median_index:]

        return ColorBox(box1_pixels, box1_counts), ColorBox(box2_pixels, box2_counts)

    def get_average_color(self) -> np.ndarray:
        """
        Get average color of the box, weighted by pixel counts.

        Returns:
            RGB array representing average color
        """
        if len(self.pixels) == 0:
            return np.array([0, 0, 0])

        # Weighted average
        total_count = np.sum(self.counts)
        if total_count == 0:
            return np.mean(self.pixels, axis=0)

        weighted_sum = np.sum(self.pixels * self.counts[:, np.newaxis], axis=0)
        return weighted_sum / total_count