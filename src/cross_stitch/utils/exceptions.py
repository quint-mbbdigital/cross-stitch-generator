"""Custom exceptions for cross-stitch pattern generation."""

from typing import Optional


class CrossStitchError(Exception):
    """Base exception for all cross-stitch pattern generation errors."""

    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.message = message
        self.cause = cause

    def __str__(self) -> str:
        if self.cause:
            return f"{self.message} (caused by: {self.cause})"
        return self.message


class ValidationError(CrossStitchError):
    """Raised when input validation fails."""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Optional[str] = None
    ) -> None:
        super().__init__(message)
        self.field = field
        self.value = value

    def __str__(self) -> str:
        if self.field and self.value is not None:
            return f"Validation error for '{self.field}': {self.message} (value: {self.value})"
        elif self.field:
            return f"Validation error for '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class ImageProcessingError(CrossStitchError):
    """Raised when image processing operations fail."""

    def __init__(
        self,
        message: str,
        image_path: Optional[str] = None,
        operation: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, cause)
        self.image_path = image_path
        self.operation = operation

    def __str__(self) -> str:
        parts = ["Image processing error"]
        if self.operation:
            parts.append(f"during {self.operation}")
        if self.image_path:
            parts.append(f"for '{self.image_path}'")
        parts.append(f": {self.message}")

        result = " ".join(parts)
        if self.cause:
            result += f" (caused by: {self.cause})"
        return result


class ColorQuantizationError(CrossStitchError):
    """Raised when color quantization fails."""

    def __init__(
        self,
        message: str,
        method: Optional[str] = None,
        max_colors: Optional[int] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, cause)
        self.method = method
        self.max_colors = max_colors

    def __str__(self) -> str:
        parts = ["Color quantization error"]
        if self.method:
            parts.append(f"using {self.method}")
        if self.max_colors is not None:
            parts.append(f"with {self.max_colors} colors")
        parts.append(f": {self.message}")

        result = " ".join(parts)
        if self.cause:
            result += f" (caused by: {self.cause})"
        return result


class ExcelGenerationError(CrossStitchError):
    """Raised when Excel file generation fails."""

    def __init__(
        self,
        message: str,
        output_path: Optional[str] = None,
        sheet_name: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, cause)
        self.output_path = output_path
        self.sheet_name = sheet_name

    def __str__(self) -> str:
        parts = ["Excel generation error"]
        if self.sheet_name:
            parts.append(f"for sheet '{self.sheet_name}'")
        if self.output_path:
            parts.append(f"at '{self.output_path}'")
        parts.append(f": {self.message}")

        result = " ".join(parts)
        if self.cause:
            result += f" (caused by: {self.cause})"
        return result


class FileOperationError(CrossStitchError):
    """Raised when file operations fail."""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, cause)
        self.file_path = file_path
        self.operation = operation

    def __str__(self) -> str:
        parts = ["File operation error"]
        if self.operation:
            parts.append(f"during {self.operation}")
        if self.file_path:
            parts.append(f"for '{self.file_path}'")
        parts.append(f": {self.message}")

        result = " ".join(parts)
        if self.cause:
            result += f" (caused by: {self.cause})"
        return result


class ConfigurationError(CrossStitchError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, setting: Optional[str] = None) -> None:
        super().__init__(message)
        self.setting = setting

    def __str__(self) -> str:
        if self.setting:
            return f"Configuration error for '{self.setting}': {self.message}"
        return f"Configuration error: {self.message}"


class PatternGenerationError(CrossStitchError):
    """Raised when pattern generation fails."""

    def __init__(
        self,
        message: str,
        resolution: Optional[str] = None,
        stage: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, cause)
        self.resolution = resolution
        self.stage = stage

    def __str__(self) -> str:
        parts = ["Pattern generation error"]
        if self.stage:
            parts.append(f"during {self.stage}")
        if self.resolution:
            parts.append(f"for resolution {self.resolution}")
        parts.append(f": {self.message}")

        result = " ".join(parts)
        if self.cause:
            result += f" (caused by: {self.cause})"
        return result
