"""Texture detection module for identifying problematic background patterns."""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import numpy as np
from PIL import Image


@dataclass
class TextureWarning:
    """Model for texture detection warnings."""

    has_problematic_texture: bool = False
    warning_message: str = ""
    confidence_score: float = 0.0
    detection_details: Optional[Dict[str, Any]] = field(default_factory=dict)


class TextureDetector:
    """Detects problematic texture patterns that could cause poor cross-stitch results."""

    def __init__(self):
        """Initialize texture detector."""
        self.variance_threshold = 200.0  # High pixel-to-pixel variance
        self.unique_color_threshold = 15  # Many unique colors in small region
        self.confidence_threshold = 0.6  # Minimum confidence for warning

    def analyze_texture(self, image: Image.Image) -> TextureWarning:
        """
        Analyze image for problematic textures.

        Args:
            image: PIL Image to analyze

        Returns:
            TextureWarning with analysis results
        """
        try:
            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Get image as numpy array
            img_array = np.array(image)

            # Run detection methods
            variance_score = self.detect_color_variance(img_array)
            cluster_score = self.detect_clustered_colors(img_array)
            frequency_score = self.detect_high_frequency_patterns(img_array)

            # Calculate overall confidence score
            confidence = max(variance_score, cluster_score, frequency_score)

            detection_details = {
                "color_variance": variance_score,
                "clustered_colors": cluster_score,
                "high_frequency": frequency_score,
            }

            # Determine if texture is problematic
            has_texture = confidence > self.confidence_threshold

            warning_message = ""
            if has_texture:
                warning_message = self._generate_warning_message(
                    detection_details, confidence
                )

            return TextureWarning(
                has_problematic_texture=has_texture,
                warning_message=warning_message,
                confidence_score=confidence,
                detection_details=detection_details,
            )

        except Exception as e:
            # Return safe default if analysis fails
            return TextureWarning(
                has_problematic_texture=False,
                warning_message="",
                confidence_score=0.0,
                detection_details={"error": str(e)},
            )

    def detect_color_variance(self, img_array: np.ndarray) -> float:
        """
        Detect high color variance in visually uniform regions.

        Args:
            img_array: Image as numpy array (H, W, 3)

        Returns:
            Confidence score (0.0-1.0) for variance-based texture detection
        """
        try:
            height, width = img_array.shape[:2]

            # Sample background regions (corners and edges)
            region_size = min(height // 6, width // 6, 30)  # 30 pixel max region
            if region_size < 10:
                return 0.0  # Image too small for meaningful analysis

            regions = [
                # Corners
                img_array[:region_size, :region_size],  # Top-left
                img_array[:region_size, -region_size:],  # Top-right
                img_array[-region_size:, :region_size],  # Bottom-left
                img_array[-region_size:, -region_size:],  # Bottom-right
                # Center edges
                img_array[
                    :region_size,
                    width // 2 - region_size // 2 : width // 2 + region_size // 2,
                ],  # Top center
                img_array[
                    -region_size:,
                    width // 2 - region_size // 2 : width // 2 + region_size // 2,
                ],  # Bottom center
            ]

            variance_scores = []

            for region in regions:
                if region.size == 0:
                    continue

                # Calculate pixel-to-pixel variance
                # Look at differences between adjacent pixels
                h_diff = np.diff(region, axis=0)  # Horizontal differences
                v_diff = np.diff(region, axis=1)  # Vertical differences

                # Calculate variance of differences (high = textured)
                h_variance = np.var(h_diff)
                v_variance = np.var(v_diff)
                avg_variance = (h_variance + v_variance) / 2

                # Also check overall color uniformity
                color_std = np.std(region.reshape(-1, 3), axis=0).mean()

                # Check for gradient patterns
                h_diff_mean = np.mean(np.abs(h_diff))
                v_diff_mean = np.mean(np.abs(v_diff))

                # Detect gradients: one direction has consistent change, other has minimal change
                is_horizontal_gradient = (
                    h_diff_mean > 5 and v_diff_mean < 2
                )  # Changes horizontally, not vertically
                is_vertical_gradient = (
                    v_diff_mean > 5 and h_diff_mean < 2
                )  # Changes vertically, not horizontally

                # Also check for smooth gradients with consistent direction
                if h_diff_mean > 5 or v_diff_mean > 5:  # Significant color changes
                    h_diff_variance = np.var(np.abs(h_diff)) if h_diff_mean > 0 else 0
                    v_diff_variance = np.var(np.abs(v_diff)) if v_diff_mean > 0 else 0

                    # For gradients, the changing direction should have low variance (consistent)
                    # and the non-changing direction should have minimal change
                    is_smooth_gradient = False
                    if (
                        h_diff_mean > v_diff_mean and h_diff_variance < 50
                    ):  # Horizontal gradient
                        is_smooth_gradient = True
                    elif (
                        v_diff_mean > h_diff_mean and v_diff_variance < 50
                    ):  # Vertical gradient
                        is_smooth_gradient = True

                    if (
                        is_horizontal_gradient
                        or is_vertical_gradient
                        or is_smooth_gradient
                    ):
                        continue  # Skip this region, it's likely a gradient

                # High variance with moderate color difference suggests texture
                # Skip if completely uniform (solid color) or identified as gradient
                if 3 < color_std < 50:  # Relatively uniform but not flat
                    variance_score = min(avg_variance / self.variance_threshold, 1.0)
                    variance_scores.append(variance_score)

            if not variance_scores:
                return 0.0

            # Return highest variance score found
            return max(variance_scores)

        except Exception:
            return 0.0

    def detect_clustered_colors(self, img_array: np.ndarray) -> float:
        """
        Detect many colors clustered within small color distances.

        Args:
            img_array: Image as numpy array (H, W, 3)

        Returns:
            Confidence score (0.0-1.0) for clustered color detection
        """
        try:
            height, width = img_array.shape[:2]

            # Sample a representative region from center
            center_y, center_x = height // 2, width // 2
            sample_size = min(height // 4, width // 4, 50)

            if sample_size < 20:
                return 0.0

            # Extract center region
            y1 = max(0, center_y - sample_size // 2)
            y2 = min(height, center_y + sample_size // 2)
            x1 = max(0, center_x - sample_size // 2)
            x2 = min(width, center_x + sample_size // 2)

            region = img_array[y1:y2, x1:x2]

            # Get unique colors in region
            pixels = region.reshape(-1, 3)
            unique_colors = np.unique(pixels, axis=0)

            # Count colors that are very similar to each other
            similar_color_count = 0
            total_colors = len(unique_colors)

            if total_colors < 5:
                return 0.0  # Too few colors to be textured

            for i, color1 in enumerate(unique_colors):
                for j, color2 in enumerate(unique_colors[i + 1 :], i + 1):
                    # Calculate Euclidean distance in RGB space
                    distance = np.sqrt(
                        np.sum((color1.astype(float) - color2.astype(float)) ** 2)
                    )

                    # Colors are "similar" if distance is small (texture creates many similar colors)
                    if distance < 25:  # Very similar colors
                        similar_color_count += 1

            # High ratio of similar colors suggests texture
            # But check if this might be a smooth gradient first
            pixels_sorted = pixels[
                np.lexsort((pixels[:, 2], pixels[:, 1], pixels[:, 0]))
            ]
            gradient_check = np.diff(pixels_sorted.astype(float), axis=0)
            avg_gradient = np.mean(np.linalg.norm(gradient_check, axis=1))

            # If gradient is very smooth (consistent color progression), it's likely a gradient
            if (
                avg_gradient > 3 and total_colors > self.unique_color_threshold
            ):  # Exclude smooth gradients
                similarity_ratio = similar_color_count / (
                    total_colors * (total_colors - 1) / 2
                )
                return min(similarity_ratio * 2, 1.0)  # Reduce signal strength

            return 0.0

        except Exception:
            return 0.0

    def detect_high_frequency_patterns(self, img_array: np.ndarray) -> float:
        """
        Detect repeating high-frequency patterns.

        Args:
            img_array: Image as numpy array (H, W, 3)

        Returns:
            Confidence score (0.0-1.0) for high frequency pattern detection
        """
        try:
            # Convert to grayscale for pattern analysis
            gray = np.mean(img_array, axis=2)

            # Use simple edge detection to find high-frequency content
            # Calculate gradients
            grad_x = np.abs(np.diff(gray, axis=1))
            grad_y = np.abs(np.diff(gray, axis=0))

            # Count high-gradient pixels (edges)
            edge_threshold = np.std(gray) * 0.5  # Adaptive threshold

            if edge_threshold < 1.0:
                return 0.0  # Very uniform image

            edge_pixels_x = np.sum(grad_x > edge_threshold)
            edge_pixels_y = np.sum(grad_y > edge_threshold)

            total_pixels = gray.size
            edge_density = (edge_pixels_x + edge_pixels_y) / (2 * total_pixels)

            # High edge density suggests textured/patterned background
            # Typical fabric/texture has 10-30% edge pixels
            if edge_density > 0.15:  # 15% threshold
                return min((edge_density - 0.15) / 0.15, 1.0)

            return 0.0

        except Exception:
            return 0.0

    def _generate_warning_message(
        self, detection_details: Dict[str, float], confidence: float
    ) -> str:
        """Generate helpful warning message based on detection results."""

        primary_cause = max(detection_details.items(), key=lambda x: x[1])
        cause_name, cause_score = primary_cause

        # Base warning message
        if cause_name == "color_variance":
            base_msg = "Detected textured background with high pixel variation"
        elif cause_name == "clustered_colors":
            base_msg = "Detected fabric-like background with many similar colors"
        elif cause_name == "high_frequency":
            base_msg = "Detected patterned background with repeating elements"
        else:
            base_msg = "Detected problematic background texture"

        # Add confidence indicator
        if confidence > 0.8:
            confidence_text = " (high confidence)"
        elif confidence > 0.7:
            confidence_text = " (medium confidence)"
        else:
            confidence_text = " (low confidence)"

        # Add helpful suggestions
        suggestions = [
            "Consider pre-processing the image to blur or smooth the background",
            "Try using fewer colors with --max-colors 5-10 to reduce noise",
            "For fabric textures, consider removing or masking the background",
        ]

        suggestion_text = ". ".join(suggestions)

        return f"{base_msg}{confidence_text}. {suggestion_text}."
