/**
 * HTMX and Alpine.js interaction handlers.
 */

// Auto-generation workflow is now handled in upload-handler.js
// This file now focuses on manual regeneration and UI interactions

// Regenerate pattern functionality moved to Alpine.js app state in base.html

// Listen for magic-moment events - ANIMATION DISABLED for instant rendering
document.addEventListener('magic-moment', (event) => {
    const detail = event.detail || {};

    if (detail.data && PatternStore) {
        // Initialize and load pattern WITHOUT animation effects
        PatternStore.init('pattern-canvas');
        PatternStore.load(detail.data);

        // Animation effects disabled - no CSS class manipulation
        // const canvas = document.getElementById('pattern-canvas');
        // if (canvas) {
        //     canvas.classList.add('magic-moment');
        //     setTimeout(() => {
        //         canvas.classList.remove('magic-moment');
        //     }, 1200);
        // }
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
            dmc_only: app.config.dmc_only,

            // Added 7 new parameters
            max_merge_distance: app.config.max_merge_distance,
            resolutions: app.config.resolutions,
            excel_cell_size: app.config.excel_cell_size,
            include_color_legend: app.config.include_color_legend,
            legend_sheet_name: app.config.legend_sheet_name,
            dmc_palette_size: app.config.dmc_palette_size,
            dmc_database: app.config.dmc_database
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

    if (detail.data) {
        // New pattern data - initialize and load
        PatternStore.init('pattern-canvas');
        PatternStore.load(detail.data);
    } else if (detail.mode && PatternStore.data) {
        // Just changing render mode
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
                }

                // Render pattern instantly without animation effects
                document.dispatchEvent(new CustomEvent('render-pattern', {
                    detail: { data: patternData, mode: app.viewMode }
                }));
            } catch (e) {
                console.error('Failed to parse pattern data from HTMX response:', e);
            }
        }
    }
});