/**
 * Display Effects Manager: Streamlined control for cross-stitch pattern display effects.
 *
 * Manages visual effects during pattern display including canvas resize animations,
 * magic moment reveals, container transitions, and zoom transformations.
 */

const DisplayEffectsManager = {
    // Base effect configuration
    baseConfig: {
        canvas: {
            resizeAnimation: { enabled: true, duration: 200, easing: 'ease-out' },
            preSize: true,
            smoothTransitions: true
        },
        magicMoment: {
            enabled: true,
            duration: 1200,
            effects: { blur: { from: 8, to: 0 }, scale: { from: 0.95, to: 1 }, opacity: { from: 0, to: 1 } },
            easing: 'ease-out'
        },
        transitions: {
            containerFade: { enabled: true, duration: 200, easing: 'ease-out' }
        },
        zoom: { smooth: true, duration: 150, easing: 'ease-out' }
    },

    // Preset configurations using generator function
    createPreset(overrides = {}) {
        const preset = JSON.parse(JSON.stringify(this.baseConfig)); // Deep clone
        return this._mergeDeep(preset, overrides);
    },

    presets: {
        default: null, // Will be set to baseConfig in init()

        enhanced: {
            canvas: {
                resizeAnimation: { duration: 400, easing: 'cubic-bezier(0.4, 0, 0.2, 1)' }
            },
            magicMoment: {
                duration: 2000,
                effects: { blur: { from: 12, to: 0 }, scale: { from: 0.9, to: 1 } },
                easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
            },
            transitions: {
                containerFade: { duration: 400, easing: 'cubic-bezier(0.4, 0, 0.2, 1)' }
            },
            zoom: { duration: 250, easing: 'cubic-bezier(0.4, 0, 0.2, 1)' }
        },

        minimal: {
            canvas: {
                resizeAnimation: { enabled: false, duration: 0, easing: 'none' },
                smoothTransitions: false
            },
            magicMoment: {
                enabled: false,
                duration: 0,
                effects: { blur: { from: 0, to: 0 }, scale: { from: 1, to: 1 }, opacity: { from: 1, to: 1 } },
                easing: 'none'
            },
            transitions: { containerFade: { enabled: false, duration: 0, easing: 'none' } },
            zoom: { smooth: false, duration: 0, easing: 'none' }
        }
    },

    config: null,
    currentPreset: 'default',

    /**
     * Deep merge utility for combining configurations
     */
    _mergeDeep(target, source) {
        for (const key in source) {
            if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                target[key] = target[key] || {};
                this._mergeDeep(target[key], source[key]);
            } else {
                target[key] = source[key];
            }
        }
        return target;
    },

    /**
     * Load a preset configuration
     */
    loadPreset(presetName) {
        if (presetName === 'default') {
            this.config = JSON.parse(JSON.stringify(this.baseConfig));
        } else if (this.presets[presetName]) {
            this.config = this.createPreset(this.presets[presetName]);
        } else {
            console.warn(`⚠️ Unknown preset: ${presetName}. Available:`, Object.keys(this.presets));
            return;
        }

        this.currentPreset = presetName;
        this._applyReducedMotionOverrides();
        console.log(`🎨 Display effects preset loaded: ${presetName}`);
    },

    /**
     * Apply user's reduced motion preference
     */
    _applyReducedMotionOverrides() {
        const prefersReducedMotion = window.matchMedia &&
                                   window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        if (prefersReducedMotion) {
            this.config.canvas.resizeAnimation.enabled = false;
            this.config.canvas.smoothTransitions = false;
            this.config.magicMoment.enabled = false;
            this.config.transitions.containerFade.enabled = false;
            this.config.zoom.smooth = false;
            console.log('🔇 Animations disabled due to prefers-reduced-motion');
        }
    },

    /**
     * Update configuration values directly
     */
    set(path, value) {
        const keys = path.split('.');
        let current = this.config;

        for (let i = 0; i < keys.length - 1; i++) {
            current = current[keys[i]];
        }
        current[keys[keys.length - 1]] = value;
        this.currentPreset = 'custom';
    },

    /**
     * Initialize the effects manager
     */
    init() {
        // Set up default preset
        this.presets.default = null; // Will use baseConfig
        this.loadPreset('default');

        // Listen for reduced motion changes
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
            mediaQuery.addListener(() => {
                this._applyReducedMotionOverrides();
                console.log('🔄 Reduced motion preference updated');
            });
        }

        console.log('✨ DisplayEffectsManager initialized');
    }
};

// Initialize on load
if (typeof window !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        DisplayEffectsManager.init();
    });
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DisplayEffectsManager;
}