/**
 * HTMX and Alpine.js interaction handlers.
 */

// Auto-generation workflow is now handled in upload-handler.js
// This file now focuses on manual regeneration and UI interactions

// Regenerate pattern functionality moved to Alpine.js app state in base.html

// Listen for magic-moment events (The "Darkroom" reveal)
document.addEventListener('magic-moment', (event) => {
    const detail = event.detail || {};

    if (detail.data && PatternStore && typeof DisplayEffectsManager !== 'undefined') {
        // Get effect configuration
        const effectConfig = detail.effectConfig || DisplayEffectsManager.config;
        const isInitialLoad = detail.isInitialLoad !== false; // Default to true

        console.log('🎭 Magic moment triggered:', { isInitialLoad, effectConfig: effectConfig });

        // Initialize and load pattern with effects
        PatternStore.init('pattern-canvas');

        // Pre-size canvas if enabled
        const canvasConfig = DisplayEffectsManager.getCanvasConfig(isInitialLoad);
        if (canvasConfig.preSize) {
            PatternStore.preSize(detail.data, canvasConfig);
        }

        // Load pattern data
        PatternStore.data = detail.data;
        PatternStore.gridBuffer = new Uint8ClampedArray(detail.data.grid);

        // Apply magic moment effect to canvas if enabled
        const canvas = document.getElementById('pattern-canvas');
        const canvasContainer = canvas?.parentElement;

        if (canvas && canvasContainer) {
            const magicConfig = DisplayEffectsManager.getMagicMomentConfig();

            // Check if canvas container is visible (Alpine.js x-show)
            const containerVisible = !canvasContainer.hasAttribute('style') ||
                                   !canvasContainer.style.display.includes('none');

            console.log('🎭 Magic moment canvas check:', {
                canvasExists: !!canvas,
                containerVisible,
                magicEnabled: magicConfig.enabled
            });

            if (magicConfig.enabled && containerVisible) {
                // Apply magic moment CSS class with custom duration
                canvas.classList.add('magic-moment');

                // Update CSS custom property for dynamic duration if needed
                canvas.style.setProperty('--magic-duration', `${magicConfig.duration}ms`);

                console.log(`✨ Magic moment animation applied (${magicConfig.duration}ms)`);

                // Remove class after animation
                setTimeout(() => {
                    canvas.classList.remove('magic-moment');
                    canvas.style.removeProperty('--magic-duration');
                    console.log('🎭 Magic moment animation completed');
                }, magicConfig.duration);
            } else if (!containerVisible) {
                console.log('⚠️ Canvas container not visible, retrying magic moment in 50ms');
                // Retry after a short delay to allow Alpine.js to update
                setTimeout(() => {
                    document.dispatchEvent(new CustomEvent('magic-moment', {
                        detail: { data: detail.data, isInitialLoad, effectConfig }
                    }));
                }, 50);
            }
        }

        // Render with effects
        PatternStore.renderWithEffects('color', canvasConfig, isInitialLoad);
    } else if (detail.data && PatternStore) {
        // Fallback to original behavior if DisplayEffectsManager not available
        console.log('⚠️ DisplayEffectsManager not available, using fallback behavior');
        PatternStore.init('pattern-canvas');
        PatternStore.load(detail.data);

        const canvas = document.getElementById('pattern-canvas');
        const canvasContainer = canvas?.parentElement;

        if (canvas && canvasContainer) {
            // Check if canvas container is visible
            const containerVisible = !canvasContainer.hasAttribute('style') ||
                                   !canvasContainer.style.display.includes('none');

            if (containerVisible) {
                canvas.classList.add('magic-moment');
                console.log('✨ Fallback magic moment animation applied');
                setTimeout(() => {
                    canvas.classList.remove('magic-moment');
                    console.log('🎭 Fallback magic moment animation completed');
                }, 1200);
            } else {
                console.log('⚠️ Canvas container not visible, retrying fallback magic moment in 50ms');
                setTimeout(() => {
                    document.dispatchEvent(new CustomEvent('magic-moment', {
                        detail: { data: detail.data, isInitialLoad: true }
                    }));
                }, 50);
            }
        }
    }
});

// Listen for export-pattern event
document.addEventListener('export-pattern', async (event) => {
    const app = Alpine.$data(document.querySelector('[x-data="appState()"]'));

    // Validate requirements for export
    if (!app.jobId) {
        showNotification('Connection lost. Please refresh and try again.', 'error');
        return;
    }

    if (!app.patternData) {
        showNotification('No pattern to export. Please generate a pattern first.', 'error');
        return;
    }

    try {
        // Show export in progress (subtle feedback)
        const exportButton = event.target.closest('button') || document.querySelector('[data-export-button]');
        if (exportButton) {
            const originalContent = exportButton.innerHTML;
            exportButton.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Exporting...';
            exportButton.disabled = true;

            // Restore button after export
            setTimeout(() => {
                exportButton.innerHTML = originalContent;
                exportButton.disabled = false;
                lucide.createIcons(); // Refresh icons
            }, 2000);
        }

        // Build download URL with current config
        const params = new URLSearchParams({
            // Current 8 parameters
            resolution: app.config.resolution,
            max_colors: app.config.max_colors,
            quantization: app.config.quantization,
            edge_mode: app.config.edge_mode,
            transparency: app.config.transparency,
            min_color_percent: app.config.min_color_percent,
            enable_dmc: app.config.enable_dmc,
            dmc_only: app.config.dmc_only
        });

        const downloadUrl = `/api/download/${app.jobId}?${params.toString()}`;

        // Create temporary link to trigger download
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `cross_stitch_pattern_${app.config.resolution}x${app.config.resolution}.xlsx`;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        console.log('Export initiated successfully');

    } catch (error) {
        showNotification('Export failed. Please try again.', 'error');
        console.error('Export error:', error);

        // Restore button on error
        const exportButton = event.target.closest('button') || document.querySelector('[data-export-button]');
        if (exportButton) {
            exportButton.innerHTML = '<i data-lucide="download" class="w-4 h-4"></i> Export';
            exportButton.disabled = false;
            lucide.createIcons();
        }
    }
});

// Listen for render-pattern events (both new patterns and mode changes)
document.addEventListener('render-pattern', (event) => {
    const detail = event.detail || {};

    if (detail.data && typeof DisplayEffectsManager !== 'undefined') {
        // New pattern data - initialize and load with effects
        const effectConfig = detail.effectConfig || DisplayEffectsManager.config;
        const isInitialLoad = detail.isInitialLoad !== false; // Default to true

        console.log('🎨 Render pattern triggered (new data):', { isInitialLoad });

        PatternStore.init('pattern-canvas');

        // Pre-size canvas if enabled
        const canvasConfig = DisplayEffectsManager.getCanvasConfig(isInitialLoad);
        if (canvasConfig.preSize) {
            PatternStore.preSize(detail.data, canvasConfig);
        }

        // Load pattern data
        PatternStore.data = detail.data;
        PatternStore.gridBuffer = new Uint8ClampedArray(detail.data.grid);

        // Render with effects
        PatternStore.renderWithEffects(detail.mode || 'color', canvasConfig, isInitialLoad);
    } else if (detail.data) {
        // Fallback for new pattern data without effects
        console.log('⚠️ DisplayEffectsManager not available for new pattern, using fallback');
        PatternStore.init('pattern-canvas');
        PatternStore.load(detail.data);
    } else if (detail.mode && PatternStore.data && typeof DisplayEffectsManager !== 'undefined') {
        // Just changing render mode - use effects but no re-initialization
        const canvasConfig = DisplayEffectsManager.getCanvasConfig(false); // Not initial load
        console.log('🔄 Render mode change:', detail.mode);

        PatternStore.renderWithEffects(detail.mode, canvasConfig, false);
    } else if (detail.mode && PatternStore.data) {
        // Fallback for mode change without effects
        console.log('⚠️ DisplayEffectsManager not available for mode change, using fallback');
        PatternStore.render(detail.mode);
    }
});

// Canvas hover for cell info
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('pattern-canvas');
    if (canvas) {
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const cell = PatternStore.getCellAt(x, y);
            if (cell && cell.thread) {
                canvas.title = `${cell.thread.dmc_code}: ${cell.thread.name}`;
            } else {
                canvas.title = '';
            }
        });
    }
});

// HTMX event handlers for legend synchronization
document.addEventListener('htmx:afterSwap', (event) => {
    // Refresh Lucide icons after HTMX OOB updates
    if (event.detail.target.id === 'legend-content') {
        lucide.createIcons();
    }
});

// Listen for successful pattern generation via HTMX
document.addEventListener('htmx:afterRequest', (event) => {
    if (event.detail.xhr.status === 200 && event.detail.xhr.responseText.includes('pattern-data')) {
        // Pattern generated successfully via HTMX
        const response = event.detail.xhr.responseText;

        // Extract pattern data if available
        const patternDataMatch = response.match(/data-pattern-json='([^']+)'/);
        if (patternDataMatch) {
            try {
                const patternData = JSON.parse(patternDataMatch[1]);

                // Update Alpine.js state for export functionality
                const app = Alpine.$data(document.querySelector('[x-data="appState()"]'));
                if (app) {
                    app.patternData = patternData;
                    // Ensure jobId is preserved for export
                    console.log('Pattern data synchronized for export. JobId:', app.jobId);

                    // Wait for Alpine.js to update the DOM before triggering animation
                    // This ensures x-show="patternData" becomes true and canvas container is visible
                    app.$nextTick(() => {
                        // Trigger magic moment reveal (this is initial load from file upload)
                        app.$dispatch('magic-moment', {
                            data: patternData,
                            isInitialLoad: true,  // This is the first generation from uploaded image
                            effectConfig: typeof DisplayEffectsManager !== 'undefined' ? DisplayEffectsManager.config : null
                        });

                        // Preserve current view mode (same as regenerate pattern flow)
                        app.$dispatch('render-pattern', { mode: app.viewMode });
                    });
                } else {
                    // Fallback if Alpine.js app not found
                    console.warn('⚠️ Alpine.js app not found, triggering magic moment directly');
                    document.dispatchEvent(new CustomEvent('magic-moment', {
                        detail: {
                            data: patternData,
                            isInitialLoad: true,
                            effectConfig: typeof DisplayEffectsManager !== 'undefined' ? DisplayEffectsManager.config : null
                        }
                    }));

                    // Also trigger render pattern to preserve view mode
                    document.dispatchEvent(new CustomEvent('render-pattern', {
                        detail: { mode: 'color' } // Default to color mode
                    }));
                }
            } catch (e) {
                console.error('Failed to parse pattern data from HTMX response:', e);
            }
        }
    }
});