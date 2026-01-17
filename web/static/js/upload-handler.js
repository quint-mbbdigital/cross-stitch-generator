/**
 * File upload handling with HTMX integration.
 */

// Handle file drop on dropzone
function handleFileDrop(event) {
    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        uploadFile(file);
    }
}

// Handle file selection from input
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

// Upload file to server and auto-generate pattern (Quiet Studio approach)
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Get Alpine.js state
    const appEl = document.querySelector('[x-data]');
    const app = Alpine.$data(appEl);

    app.isGenerating = true;
    app.processingStatus = 'Processing image...';

    try {
        // Step 1: Upload image
        const uploadResponse = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            const error = await uploadResponse.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const uploadResult = await uploadResponse.json();

        // Update state with upload result
        app.jobId = uploadResult.job_id;
        app.hasImage = true;
        app.processingStatus = 'Generating pattern...';

        // Show texture warnings (only critical warnings get toasts)
        if (uploadResult.texture_warning && uploadResult.texture_warning.detected) {
            showNotification(uploadResult.texture_warning.message, 'warning');
        }

        // Step 2: Auto-generate pattern
        const generateResponse = await fetch(`/api/generate/${uploadResult.job_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(app.config)
        });

        if (!generateResponse.ok) {
            const error = await generateResponse.json();
            throw new Error(error.detail || 'Pattern generation failed');
        }

        const patternData = await generateResponse.json();

        // Update app state with pattern
        app.patternData = patternData;
        app.isGenerating = false;
        app.processingStatus = 'complete';

        // Trigger magic moment reveal
        app.$dispatch('magic-moment', { data: patternData });

    } catch (error) {
        app.isGenerating = false;
        app.processingStatus = 'error';
        // Only show toast for fatal errors
        showNotification(error.message, 'error');
        console.error('Upload/generation error:', error);
    }
}

// Notification queue system to prevent overlapping
let notificationQueue = [];
let activeNotification = null;

// Modern Atelier notification helper with queueing
function showNotification(message, type = 'info') {
    // Add to queue
    notificationQueue.push({ message, type });

    // Process queue if no active notification
    if (!activeNotification) {
        processNotificationQueue();
    }
}

function processNotificationQueue() {
    if (notificationQueue.length === 0) {
        activeNotification = null;
        return;
    }

    const { message, type } = notificationQueue.shift();
    displayNotification(message, type);
}

function displayNotification(message, type) {
    // Create toast notification with Modern Atelier styling
    const toast = document.createElement('div');
    activeNotification = toast;

    // Modern Atelier color scheme based on type
    const typeClasses = {
        info: 'bg-blue-50 text-blue-900 border-blue-200',
        warning: 'bg-amber-50 text-amber-900 border-amber-200',
        error: 'bg-red-50 text-red-900 border-red-200',
        success: 'bg-emerald-50 text-emerald-900 border-emerald-200'
    };

    const iconNames = {
        info: 'info',
        warning: 'alert-triangle',
        error: 'alert-circle',
        success: 'check-circle'
    };

    // Enhanced styling for better visibility and Modern Atelier compliance
    toast.className = `fixed bottom-6 right-6 max-w-sm shadow-lg z-50 rounded-lg border-2 ${typeClasses[type]} p-4 transition-all duration-300 transform backdrop-blur-sm`;
    toast.innerHTML = `
        <div class="flex items-start">
            <div class="flex-shrink-0 mr-3">
                <i data-lucide="${iconNames[type]}" class="w-5 h-5 mt-0.5"></i>
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold leading-relaxed">${message}</p>
            </div>
            <button onclick="dismissNotification(this)" class="ml-3 flex-shrink-0 text-current opacity-50 hover:opacity-100 transition-opacity rounded-full p-1 hover:bg-black hover:bg-opacity-10">
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>
        </div>
    `;

    // Add with slide-in animation
    toast.style.transform = 'translateY(100px) scale(0.95)';
    toast.style.opacity = '0';
    document.body.appendChild(toast);
    lucide.createIcons();

    // Trigger animation
    requestAnimationFrame(() => {
        toast.style.transform = 'translateY(0) scale(1)';
        toast.style.opacity = '1';
    });

    // Auto-remove with shorter durations to prevent queue backup
    const timeouts = {
        info: 2500,      // Informational - 2.5 seconds
        warning: 4000,   // Warnings - 4 seconds
        error: 5000,     // Errors - 5 seconds
        success: 2000    // Success - 2 seconds
    };

    setTimeout(() => {
        dismissNotification(toast.querySelector('button'));
    }, timeouts[type]);
}

function dismissNotification(button) {
    const toast = button.closest('.fixed');
    if (toast) {
        toast.style.transform = 'translateY(20px) scale(0.95)';
        toast.style.opacity = '0';
        setTimeout(() => {
            toast.remove();
            // Process next notification in queue
            setTimeout(processNotificationQueue, 100);
        }, 300);
    }
}