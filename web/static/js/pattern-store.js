/**
 * PatternStore: Centralized pattern data management.
 * Separated from Alpine.js to prevent DOM thrashing on large patterns.
 *
 * CRITICAL: Uses Uint8ClampedArray for the grid to handle 40,000+ cells
 * (200x200 patterns) without UI lag. This is essential for "Modern Atelier" snappiness.
 */
const PatternStore = {
    data: null,
    canvas: null,
    ctx: null,
    cellSize: 4,

    // Typed array for high-performance grid access
    gridBuffer: null,

    /**
     * Initialize store with canvas element.
     */
    init(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (this.canvas) {
            this.ctx = this.canvas.getContext('2d', {
                alpha: false,  // Optimization: no transparency needed
                willReadFrequently: false
            });
        }
    },

    /**
     * Load pattern data from API response.
     * Converts grid array to Uint8ClampedArray for performance.
     */
    load(patternData) {
        this.data = patternData;

        // Convert grid to typed array for fast iteration
        // This is CRITICAL for 200x200+ patterns (40,000 cells)
        this.gridBuffer = new Uint8ClampedArray(patternData.grid);

        this.render('color');
    },

    /**
     * Calculate and optionally pre-size canvas dimensions before display.
     * This prevents visual "pop" during initial pattern reveal.
     * @param {Object} patternData - Pattern data with width/height
     * @param {Object} effectConfig - Effect configuration from DisplayEffectsManager
     * @returns {Object} Calculated canvas dimensions { width, height, cellSize }
     */
    preSize(patternData, effectConfig) {
        if (!patternData || !this.canvas) return null;

        const { width, height } = patternData;

        // Calculate optimal cell size (same logic as render method)
        const maxCanvasSize = Math.min(window.innerWidth - 400, window.innerHeight - 100);
        const cellSize = Math.max(2, Math.floor(maxCanvasSize / Math.max(width, height)));

        const canvasWidth = width * cellSize;
        const canvasHeight = height * cellSize;

        // Pre-size canvas if enabled to prevent visual "pop"
        if (effectConfig && effectConfig.preSize) {
            this.canvas.width = canvasWidth;
            this.canvas.height = canvasHeight;
            this.cellSize = cellSize;
        }

        return {
            width: canvasWidth,
            height: canvasHeight,
            cellSize: cellSize
        };
    },

    /**
     * Enhanced render method that respects effect configuration.
     * @param {'color'|'symbol'} mode - Render mode
     * @param {Object} effectConfig - Effect configuration from DisplayEffectsManager
     * @param {boolean} isInitialLoad - Whether this is the first pattern load
     */
    renderWithEffects(mode = 'color', effectConfig = null, isInitialLoad = false) {
        if (!this.data || !this.ctx || !this.gridBuffer) return;

        const { width, height, palette } = this.data;

        // Calculate new dimensions
        const maxCanvasSize = Math.min(window.innerWidth - 400, window.innerHeight - 100);
        const newCellSize = Math.max(2, Math.floor(maxCanvasSize / Math.max(width, height)));
        const newWidth = width * newCellSize;
        const newHeight = height * newCellSize;

        // Check if dimensions changed
        const dimensionsChanged =
            this.canvas.width !== newWidth ||
            this.canvas.height !== newHeight ||
            this.cellSize !== newCellSize;

        if (dimensionsChanged && effectConfig && effectConfig.resizeAnimation && effectConfig.resizeAnimation.enabled) {
            // Apply resize animation
            this.applyResizeAnimation(newWidth, newHeight, newCellSize, effectConfig.resizeAnimation);
        } else {
            // Immediate resize without animation
            this.canvas.width = newWidth;
            this.canvas.height = newHeight;
            this.cellSize = newCellSize;
        }

        // Proceed with normal rendering
        this.renderPattern(mode);
    },

    /**
     * Apply smooth canvas resize animation.
     * @param {number} targetWidth - Target canvas width
     * @param {number} targetHeight - Target canvas height
     * @param {number} targetCellSize - Target cell size
     * @param {Object} animConfig - Animation configuration
     */
    applyResizeAnimation(targetWidth, targetHeight, targetCellSize, animConfig) {
        if (!animConfig.enabled || animConfig.duration <= 0) {
            // No animation, apply immediately
            this.canvas.width = targetWidth;
            this.canvas.height = targetHeight;
            this.cellSize = targetCellSize;
            return;
        }

        const startTime = performance.now();
        const startWidth = this.canvas.width;
        const startHeight = this.canvas.height;
        const startCellSize = this.cellSize;

        const widthDiff = targetWidth - startWidth;
        const heightDiff = targetHeight - startHeight;
        const cellSizeDiff = targetCellSize - startCellSize;

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / animConfig.duration, 1);

            // Apply easing function
            const easedProgress = this.applyEasing(progress, animConfig.easing);

            // Interpolate values
            this.canvas.width = Math.round(startWidth + (widthDiff * easedProgress));
            this.canvas.height = Math.round(startHeight + (heightDiff * easedProgress));
            this.cellSize = startCellSize + (cellSizeDiff * easedProgress);

            // Re-render at intermediate size
            this.renderPattern();

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                // Ensure final values are exact
                this.canvas.width = targetWidth;
                this.canvas.height = targetHeight;
                this.cellSize = targetCellSize;
                this.renderPattern();
            }
        };

        requestAnimationFrame(animate);
    },

    /**
     * Apply easing function to animation progress.
     * @param {number} progress - Animation progress (0-1)
     * @param {string} easing - Easing function name
     * @returns {number} Eased progress value
     */
    applyEasing(progress, easing) {
        switch (easing) {
            case 'ease-out':
                return 1 - Math.pow(1 - progress, 2);
            case 'ease-in':
                return Math.pow(progress, 2);
            case 'ease-in-out':
                return progress < 0.5
                    ? 2 * Math.pow(progress, 2)
                    : 1 - Math.pow(-2 * progress + 2, 2) / 2;
            case 'cubic-bezier(0.4, 0, 0.2, 1)':
                // Approximation of Material Design easing
                return progress < 0.5
                    ? 2 * progress * progress
                    : 1 - Math.pow(-2 * progress + 2, 2) / 2;
            case 'none':
            default:
                return progress;
        }
    },

    /**
     * Core pattern rendering logic (extracted from original render method).
     * @param {'color'|'symbol'} mode - Render mode
     */
    renderPattern(mode = 'color') {
        if (!this.data || !this.ctx || !this.gridBuffer) return;

        const { width, height, palette } = this.data;

        // Pre-parse palette colors for performance
        const paletteRGB = palette.map(hex => ({
            r: parseInt(hex.slice(1, 3), 16),
            g: parseInt(hex.slice(3, 5), 16),
            b: parseInt(hex.slice(5, 7), 16),
            hex: hex
        }));

        // Use ImageData for bulk pixel manipulation (fastest method)
        if (this.cellSize <= 4) {
            this.renderWithImageData(width, height, paletteRGB);
        } else {
            // For larger cells, use fillRect (allows grid lines)
            this.renderWithFillRect(width, height, paletteRGB, mode);
        }
    },

    /**
     * Render pattern to canvas using optimized buffer access.
     * @param {'color'|'symbol'} mode - Render mode
     */
    render(mode = 'color') {
        if (!this.data || !this.ctx || !this.gridBuffer) return;

        const { width, height } = this.data;

        // Calculate optimal cell size
        const maxCanvasSize = Math.min(window.innerWidth - 400, window.innerHeight - 100);
        this.cellSize = Math.max(2, Math.floor(maxCanvasSize / Math.max(width, height)));

        // Size canvas (immediate, no animation)
        this.canvas.width = width * this.cellSize;
        this.canvas.height = height * this.cellSize;

        // Use core rendering logic
        this.renderPattern(mode);
    },

    /**
     * Ultra-fast rendering using ImageData for small cell sizes.
     * Directly manipulates pixel buffer - no fillRect overhead.
     */
    renderWithImageData(width, height, paletteRGB) {
        const imageData = this.ctx.createImageData(this.canvas.width, this.canvas.height);
        const pixels = imageData.data;
        const cellSize = this.cellSize;

        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const colorIndex = this.gridBuffer[y * width + x];
                const color = paletteRGB[colorIndex];

                // Fill cell in pixel buffer
                for (let cy = 0; cy < cellSize; cy++) {
                    for (let cx = 0; cx < cellSize; cx++) {
                        const px = (x * cellSize + cx);
                        const py = (y * cellSize + cy);
                        const idx = (py * this.canvas.width + px) * 4;

                        pixels[idx] = color.r;
                        pixels[idx + 1] = color.g;
                        pixels[idx + 2] = color.b;
                        pixels[idx + 3] = 255;
                    }
                }
            }
        }

        this.ctx.putImageData(imageData, 0, 0);
    },

    /**
     * Standard rendering with fillRect for larger cells.
     * Allows grid lines and symbol overlays.
     */
    renderWithFillRect(width, height, paletteRGB, mode) {
        // Clear
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Render cells
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const colorIndex = this.gridBuffer[y * width + x];
                const color = paletteRGB[colorIndex];

                const px = x * this.cellSize;
                const py = y * this.cellSize;

                // Fill cell
                this.ctx.fillStyle = color.hex;
                this.ctx.fillRect(px, py, this.cellSize, this.cellSize);

                // Draw symbol overlay if requested
                if (mode === 'symbol' && this.cellSize >= 8) {
                    this.drawSymbol(px, py, colorIndex, color);
                }
            }
        }

        // Draw grid lines if cells are large enough
        if (this.cellSize >= 6) {
            this.drawGrid(width, height);
        }
    },

    /**
     * Draw symbol for a cell.
     */
    drawSymbol(px, py, colorIndex, color) {
        const symbols = '○●◊◆□■△▲▽▼☆★♦♠♣♥';
        const symbol = symbols[colorIndex % symbols.length];

        // Calculate luminance for contrast
        const luminance = (0.299 * color.r + 0.587 * color.g + 0.114 * color.b) / 255;
        this.ctx.fillStyle = luminance > 0.5 ? '#000000' : '#ffffff';

        this.ctx.font = `${this.cellSize * 0.7}px monospace`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(
            symbol,
            px + this.cellSize / 2,
            py + this.cellSize / 2
        );
    },

    /**
     * Draw grid lines.
     */
    drawGrid(width, height) {
        this.ctx.strokeStyle = 'rgba(0,0,0,0.1)';
        this.ctx.lineWidth = 0.5;

        // Batch path operations for performance
        this.ctx.beginPath();
        for (let x = 0; x <= width; x++) {
            this.ctx.moveTo(x * this.cellSize, 0);
            this.ctx.lineTo(x * this.cellSize, height * this.cellSize);
        }
        for (let y = 0; y <= height; y++) {
            this.ctx.moveTo(0, y * this.cellSize);
            this.ctx.lineTo(width * this.cellSize, y * this.cellSize);
        }
        this.ctx.stroke();
    },

    /**
     * Get cell info at coordinates (for hover tooltips).
     */
    getCellAt(canvasX, canvasY) {
        if (!this.data || !this.gridBuffer) return null;

        const x = Math.floor(canvasX / this.cellSize);
        const y = Math.floor(canvasY / this.cellSize);

        if (x < 0 || x >= this.data.width || y < 0 || y >= this.data.height) {
            return null;
        }

        const colorIndex = this.gridBuffer[y * this.data.width + x];
        const thread = this.data.threads.find(t => t.hex_color === this.data.palette[colorIndex]);

        return {
            x, y,
            color: this.data.palette[colorIndex],
            thread: thread || null
        };
    }
};