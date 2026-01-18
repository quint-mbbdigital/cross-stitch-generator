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
     * Pre-size canvas based on pattern data without rendering content.
     * Call this before showing the canvas to prevent visible resize effects.
     */
    preSize(patternData) {
        if (!this.canvas) return;

        const { width, height } = patternData;

        // Diagnostic logging to confirm fix
        console.log('🔍 Canvas size BEFORE preSize:', this.canvas.width, 'x', this.canvas.height);

        // Calculate optimal cell size (same logic as render)
        const maxCanvasSize = Math.min(window.innerWidth - 400, window.innerHeight - 100);
        this.cellSize = Math.max(2, Math.floor(maxCanvasSize / Math.max(width, height)));

        // Size canvas BEFORE it becomes visible
        this.canvas.width = width * this.cellSize;
        this.canvas.height = height * this.cellSize;

        console.log('✅ Canvas size AFTER preSize:', this.canvas.width, 'x', this.canvas.height);
    },

    /**
     * Load pattern data from API response.
     * Converts grid array to Uint8ClampedArray for performance.
     * Note: Canvas should be pre-sized before calling this.
     */
    load(patternData) {
        this.data = patternData;

        // Convert grid to typed array for fast iteration
        // This is CRITICAL for 200x200+ patterns (40,000 cells)
        this.gridBuffer = new Uint8ClampedArray(patternData.grid);

        this.renderIntoCurrentSize('color');
    },

    /**
     * Render pattern into current canvas size without resizing.
     * @param {'color'|'symbol'} mode - Render mode
     */
    renderIntoCurrentSize(mode = 'color') {
        if (!this.data || !this.ctx || !this.gridBuffer) return;

        const { width, height, palette } = this.data;

        // Cell size should already be calculated by preSize()
        // If not set, calculate it now (fallback)
        if (!this.cellSize) {
            const maxCanvasSize = Math.min(window.innerWidth - 400, window.innerHeight - 100);
            this.cellSize = Math.max(2, Math.floor(maxCanvasSize / Math.max(width, height)));
        }

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
     * Legacy render method that includes canvas resizing.
     * Use for mode changes where canvas is already visible.
     * @param {'color'|'symbol'} mode - Render mode
     */
    render(mode = 'color') {
        if (!this.data || !this.ctx || !this.gridBuffer) return;

        const { width, height } = this.data;

        // Calculate optimal cell size
        const maxCanvasSize = Math.min(window.innerWidth - 400, window.innerHeight - 100);
        this.cellSize = Math.max(2, Math.floor(maxCanvasSize / Math.max(width, height)));

        // Size canvas (may cause visible resize if canvas is shown)
        this.canvas.width = width * this.cellSize;
        this.canvas.height = height * this.cellSize;

        // Render content
        this.renderIntoCurrentSize(mode);
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