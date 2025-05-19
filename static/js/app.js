/**
 * InkFrame Web Application
 * Main JavaScript file
 */

// Wait for DOM to be loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize application
    const app = new InkFrameApp();
    app.init();
});

class InkFrameApp {
    constructor() {
        // Tab navigation
        this.tabs = document.querySelectorAll('.tab');
        this.tabContents = document.querySelectorAll('.tab-content');
        
        // Photo management
        this.photosContainer = document.getElementById('photos-container');
        this.photoTemplate = document.getElementById('photo-template');
        this.dropzone = document.getElementById('dropzone');
        this.fileInput = document.getElementById('file-input');
        this.uploadProgress = document.getElementById('upload-progress');
        this.progressFill = document.querySelector('.progress-fill');
        this.progressText = document.querySelector('.progress-text');
        this.refreshDisplayBtn = document.getElementById('refresh-display');
        
        // Settings management
        this.rotationInterval = document.getElementById('rotation-interval');
        this.enableDithering = document.getElementById('enable-dithering');
        this.timezone = document.getElementById('timezone');
        this.weatherCity = document.getElementById('weather-city');
        this.weatherState = document.getElementById('weather-state');
        this.weatherCountry = document.getElementById('weather-country');
        this.weatherUnits = document.getElementById('weather-units');
        this.weatherApiKey = document.getElementById('weather-api-key');
        this.testWeatherBtn = document.getElementById('test-weather');
        this.weatherResult = document.getElementById('weather-result');
        this.saveSettingsBtn = document.getElementById('save-settings');
        
        // System information
        this.diskFill = document.querySelector('.disk-fill');
        this.diskText = document.querySelector('.disk-text');
        this.statusIndicator = document.querySelector('.indicator');
        this.statusText = document.querySelector('.status-text');
        this.uptimeEl = document.getElementById('uptime');
        this.cpuTempEl = document.getElementById('cpu-temp');
        this.photoCountEl = document.getElementById('photo-count');
        this.lastUpdateEl = document.getElementById('last-update');
        this.systemLogsEl = document.getElementById('system-logs');
        this.refreshStatusBtn = document.getElementById('refresh-status');
        this.startServiceBtn = document.getElementById('start-service');
        
        // Notifications
        this.notifications = document.getElementById('notifications');
    }
    
    init() {
        // Initialize tab navigation
        this.initTabs();
        
        // Initialize photo management
        this.initPhotoManagement();
        
        // Initialize settings
        this.initSettings();
        
        // Initialize system information
        this.initSystemInfo();
        
        // Load the active tab data
        this.loadTabData(this.getActiveTab());
    }
    
    initTabs() {
        // Add click event listeners to tabs
        this.tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs
                this.tabs.forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked tab
                tab.classList.add('active');
                
                // Hide all tab contents
                this.tabContents.forEach(content => content.classList.remove('active'));
                
                // Show the selected tab content
                const tabId = tab.getAttribute('data-tab');
                document.getElementById(tabId).classList.add('active');
                
                // Load tab data
                this.loadTabData(tabId);
            });
        });
    }
    
    getActiveTab() {
        // Get the active tab
        const activeTab = document.querySelector('.tab.active');
        return activeTab ? activeTab.getAttribute('data-tab') : 'photos';
    }
    
    loadTabData(tabId) {
        // Load data for the active tab
        switch (tabId) {
            case 'photos':
                this.loadPhotos();
                break;
            case 'settings':
                this.loadSettings();
                break;
            case 'system':
                this.loadSystemInfo();
                break;
        }
    }
    
    initPhotoManagement() {
        // Initialize dropzone for file uploads
        this.dropzone.addEventListener('click', () => {
            this.fileInput.click();
        });
        
        this.dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.dropzone.classList.add('drag-over');
        });
        
        this.dropzone.addEventListener('dragleave', () => {
            this.dropzone.classList.remove('drag-over');
        });
        
        this.dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.dropzone.classList.remove('drag-over');
            
            if (e.dataTransfer.files.length > 0) {
                this.uploadFiles(e.dataTransfer.files);
            }
        });
        
        this.fileInput.addEventListener('change', () => {
            if (this.fileInput.files.length > 0) {
                this.uploadFiles(this.fileInput.files);
            }
        });
        
        // Refresh display button
        this.refreshDisplayBtn.addEventListener('click', () => {
            this.refreshDisplay();
        });
    }
    
    initSettings() {
        // Populate timezone dropdown
        this.populateTimezones();
        
        // Test weather button
        this.testWeatherBtn.addEventListener('click', () => {
            this.testWeather();
        });
        
        // Save settings button
        this.saveSettingsBtn.addEventListener('click', () => {
            this.saveSettings();
        });
    }
    
    initSystemInfo() {
        // Refresh status button
        this.refreshStatusBtn.addEventListener('click', () => {
            this.loadSystemInfo();
        });
        
        // Start service button
        this.startServiceBtn.addEventListener('click', () => {
            this.startService();
        });
    }
    
    async loadPhotos() {
        try {
            // Show loading indicator
            this.photosContainer.innerHTML = '<div class="loading">Loading photos...</div>';
            
            // Fetch photos from the API
            const response = await fetch('/api/photos');
            const data = await response.json();
            
            // Clear the container
            this.photosContainer.innerHTML = '';
            
            if (data.photos && data.photos.length > 0) {
                // Display each photo
                data.photos.forEach(photo => {
                    this.addPhotoToGallery(photo);
                });
            } else {
                // No photos found
                this.photosContainer.innerHTML = '<div class="loading">No photos found. Upload some photos to get started.</div>';
            }
        } catch (error) {
            console.error('Error loading photos:', error);
            this.showNotification('Error loading photos. Please try again.', 'error');
            this.photosContainer.innerHTML = '<div class="loading">Error loading photos. Please try again.</div>';
        }
    }
    
    addPhotoToGallery(photo) {
        // Clone the photo template
        const template = this.photoTemplate.content.cloneNode(true);
        const item = template.querySelector('.photo-item');
        
        // Set photo details
        const img = template.querySelector('img');
        img.src = photo.thumbnail;
        img.alt = photo.name;
        
        const name = template.querySelector('.photo-name');
        name.textContent = photo.name;
        
        const date = template.querySelector('.photo-date');
        date.textContent = this.formatDate(photo.date_added);
        
        // Add delete button functionality
        const deleteBtn = template.querySelector('.delete-photo');
        deleteBtn.addEventListener('click', () => {
            this.deletePhoto(photo.id);
        });
        
        // Add to gallery
        this.photosContainer.appendChild(template);
    }
    
    async uploadFiles(files) {
        // Show progress
        this.uploadProgress.classList.remove('hidden');
        this.progressFill.style.width = '0%';
        this.progressText.textContent = 'Uploading... 0%';
        
        // Disable dropzone
        this.dropzone.style.pointerEvents = 'none';
        this.dropzone.style.opacity = '0.5';
        
        let uploadedCount = 0;
        const totalFiles = files.length;
        
        for (let i = 0; i < totalFiles; i++) {
            try {
                const file = files[i];
                
                // Check if file type is allowed
                const fileExt = file.name.split('.').pop().toLowerCase();
                const allowedExt = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'heic', 'heif'];
                
                if (!allowedExt.includes(fileExt)) {
                    this.showNotification(`File type not allowed: ${fileExt}`, 'error');
                    continue;
                }
                
                // Create form data
                const formData = new FormData();
                formData.append('file', file);
                
                // Upload file
                const response = await fetch('/api/photos', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    uploadedCount++;
                    
                    // Update progress
                    const progress = Math.round((uploadedCount / totalFiles) * 100);
                    this.progressFill.style.width = `${progress}%`;
                    this.progressText.textContent = `Uploading... ${progress}%`;
                    
                    if (i === totalFiles - 1) {
                        this.showNotification('Files uploaded successfully!', 'success');
                    }
                } else {
                    this.showNotification(`Error uploading ${file.name}: ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('Error uploading file:', error);
                this.showNotification('Error uploading file. Please try again.', 'error');
            }
        }
        
        // Re-enable dropzone
        this.dropzone.style.pointerEvents = '';
        this.dropzone.style.opacity = '';
        
        // Reset file input
        this.fileInput.value = '';
        
        // Hide progress after a delay
        setTimeout(() => {
            this.uploadProgress.classList.add('hidden');
        }, 2000);
        
        // Reload photos
        if (uploadedCount > 0) {
            this.loadPhotos();
        }
    }
    
    async deletePhoto(photoId) {
        if (confirm('Are you sure you want to delete this photo?')) {
            try {
                const response = await fetch(`/api/photos/${photoId}`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    this.showNotification('Photo deleted successfully!', 'success');
                    this.loadPhotos();
                } else {
                    this.showNotification(`Error deleting photo: ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('Error deleting photo:', error);
                this.showNotification('Error deleting photo. Please try again.', 'error');
            }
        }
    }
    
    async refreshDisplay() {
        try {
            this.refreshDisplayBtn.disabled = true;
            this.refreshDisplayBtn.textContent = 'Refreshing...';
            
            const response = await fetch('/api/refresh', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('Display refreshed with a new photo!', 'success');
            } else {
                this.showNotification(`Error refreshing display: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error refreshing display:', error);
            this.showNotification('Error refreshing display. Please try again.', 'error');
        } finally {
            this.refreshDisplayBtn.disabled = false;
            this.refreshDisplayBtn.textContent = 'Refresh Display';
        }
    }
    
    async loadSettings() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            
            if (data.config) {
                const config = data.config;
                
                // Display settings
                this.rotationInterval.value = config.display.rotation_interval_minutes;
                this.enableDithering.checked = config.display.enable_dithering;
                
                // Weather settings
                this.weatherCity.value = config.weather.city || '';
                this.weatherState.value = config.weather.state || '';
                this.weatherCountry.value = config.weather.country || '';
                this.weatherUnits.value = config.weather.units || 'metric';
                this.weatherApiKey.value = config.weather.api_key || '';
                
                // System settings
                if (config.system.timezone) {
                    this.timezone.value = config.system.timezone;
                }
            }
        } catch (error) {
            console.error('Error loading settings:', error);
            this.showNotification('Error loading settings. Please try again.', 'error');
        }
    }
    
    populateTimezones() {
        // List of common timezones
        const timezones = [
            "UTC",
            "America/New_York",
            "America/Chicago",
            "America/Denver",
            "America/Los_Angeles",
            "America/Anchorage",
            "America/Honolulu",
            "America/Toronto",
            "America/Vancouver",
            "Europe/London",
            "Europe/Paris",
            "Europe/Berlin",
            "Europe/Moscow",
            "Asia/Tokyo",
            "Asia/Shanghai",
            "Asia/Singapore",
            "Australia/Sydney",
            "Pacific/Auckland"
        ];
        
        // Clear the dropdown
        this.timezone.innerHTML = '';
        
        // Add timezone options
        timezones.forEach(tz => {
            const option = document.createElement('option');
            option.value = tz;
            option.textContent = tz;
            this.timezone.appendChild(option);
        });
    }
    
    async testWeather() {
        // Get the weather settings
        const city = this.weatherCity.value.trim();
        const state = this.weatherState.value.trim();
        const country = this.weatherCountry.value.trim();
        const apiKey = this.weatherApiKey.value.trim();
        
        if (!city) {
            this.showNotification('Please enter a city name', 'warning');
            return;
        }
        
        if (!apiKey) {
            this.showNotification('Please enter an OpenWeatherMap API key', 'warning');
            return;
        }
        
        // Show testing indicator
        this.testWeatherBtn.disabled = true;
        this.testWeatherBtn.textContent = 'Testing...';
        this.weatherResult.classList.add('hidden');
        
        try {
            // Update the config with the new values
            await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    weather: {
                        city,
                        state,
                        country,
                        api_key: apiKey,
                        units: this.weatherUnits.value
                    }
                })
            });
            
            // Refresh the weather data
            const response = await fetch('/api/weather/refresh', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok && data.weather) {
                // Show success message
                this.weatherResult.classList.remove('hidden', 'error');
                this.weatherResult.classList.add('success');
                
                const weather = data.weather;
                const units = this.weatherUnits.value === 'metric' ? '°C' : '°F';
                
                this.weatherResult.innerHTML = `
                    <strong>Weather data received!</strong><br>
                    Location: ${weather.location}, ${weather.country}<br>
                    Temperature: ${weather.temp}${units}<br>
                    Condition: ${weather.condition} (${weather.description})
                `;
            } else {
                // Show error message
                this.weatherResult.classList.remove('hidden', 'success');
                this.weatherResult.classList.add('error');
                this.weatherResult.textContent = `Error: ${data.error || 'Failed to fetch weather data'}`;
            }
        } catch (error) {
            console.error('Error testing weather:', error);
            this.weatherResult.classList.remove('hidden', 'success');
            this.weatherResult.classList.add('error');
            this.weatherResult.textContent = 'Error: Connection failed. Please check your network.';
        } finally {
            this.testWeatherBtn.disabled = false;
            this.testWeatherBtn.textContent = 'Test Weather Data';
        }
    }
    
    async saveSettings() {
        try {
            this.saveSettingsBtn.disabled = true;
            this.saveSettingsBtn.textContent = 'Saving...';
            
            // Gather settings
            const settings = {
                display: {
                    rotation_interval_minutes: parseInt(this.rotationInterval.value) || 60,
                    enable_dithering: this.enableDithering.checked
                },
                weather: {
                    city: this.weatherCity.value.trim(),
                    state: this.weatherState.value.trim(),
                    country: this.weatherCountry.value.trim(),
                    units: this.weatherUnits.value,
                    api_key: this.weatherApiKey.value.trim()
                },
                system: {
                    timezone: this.timezone.value
                }
            };
            
            // Save settings
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('Settings saved successfully!', 'success');
            } else {
                this.showNotification(`Error saving settings: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showNotification('Error saving settings. Please try again.', 'error');
        } finally {
            this.saveSettingsBtn.disabled = false;
            this.saveSettingsBtn.textContent = 'Save Settings';
        }
    }
    
    async loadSystemInfo() {
        try {
            // Load system status
            const response = await fetch('/api/system/status');
            const data = await response.json();
            
            if (data.status) {
                const status = data.status;
                
                // Update disk usage
                const percent = status.disk.percent_used;
                this.diskFill.style.width = `${percent}%`;
                this.diskFill.style.backgroundColor = percent > 90 ? 'var(--error-color)' : 
                                                     percent > 70 ? 'var(--warning-color)' : 
                                                                   'var(--accent-color)';
                this.diskText.textContent = `${status.disk.used} used of ${status.disk.total} (${percent}%)`;
                
                // Update service status
                const isRunning = status.display_running;
                this.statusIndicator.classList.remove('running', 'stopped');
                this.statusIndicator.classList.add(isRunning ? 'running' : 'stopped');
                this.statusText.textContent = isRunning ? 'Running' : 'Stopped';
                this.startServiceBtn.disabled = isRunning;
                
                // Update system details
                this.uptimeEl.textContent = this.formatUptime(status.uptime);
                this.cpuTempEl.textContent = status.cpu_temp;
                this.photoCountEl.textContent = status.photo_count;
                this.lastUpdateEl.textContent = this.formatDate(status.timestamp);
            }
            
            // Load logs
            await this.loadLogs();
        } catch (error) {
            console.error('Error loading system info:', error);
            this.showNotification('Error loading system information. Please try again.', 'error');
        }
    }
    
    async loadLogs() {
        try {
            const response = await fetch('/api/system/logs?lines=50');
            const data = await response.json();
            
            if (data.logs) {
                this.systemLogsEl.textContent = data.logs.join('');
                
                // Scroll to bottom
                this.systemLogsEl.scrollTop = this.systemLogsEl.scrollHeight;
            } else {
                this.systemLogsEl.textContent = 'No logs available.';
            }
        } catch (error) {
            console.error('Error loading logs:', error);
            this.systemLogsEl.textContent = 'Error loading logs. Please try again.';
        }
    }
    
    async startService() {
        try {
            this.startServiceBtn.disabled = true;
            this.startServiceBtn.textContent = 'Starting...';
            
            const response = await fetch('/api/system/start', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('Display service started successfully!', 'success');
                
                // Reload system info after a short delay
                setTimeout(() => {
                    this.loadSystemInfo();
                }, 1000);
            } else {
                this.showNotification(`Error starting service: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error starting service:', error);
            this.showNotification('Error starting service. Please try again.', 'error');
        } finally {
            this.startServiceBtn.disabled = false;
            this.startServiceBtn.textContent = 'Start Service';
        }
    }
    
    formatDate(isoDate) {
        if (!isoDate) return 'Unknown';
        
        const date = new Date(isoDate);
        return date.toLocaleString();
    }
    
    formatUptime(seconds) {
        if (!seconds) return 'Unknown';
        
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        const parts = [];
        if (days > 0) parts.push(`${days} day${days !== 1 ? 's' : ''}`);
        if (hours > 0) parts.push(`${hours} hour${hours !== 1 ? 's' : ''}`);
        if (minutes > 0) parts.push(`${minutes} minute${minutes !== 1 ? 's' : ''}`);
        
        return parts.join(', ') || 'Less than a minute';
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;
        
        // Add notification to container
        this.notifications.appendChild(notification);
        
        // Add close button functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.closeNotification(notification);
        });
        
        // Auto close after 5 seconds
        setTimeout(() => {
            this.closeNotification(notification);
        }, 5000);
    }
    
    closeNotification(notification) {
        // Add hide animation
        notification.classList.add('hide');
        
        // Remove after animation completes
        setTimeout(() => {
            notification.remove();
        }, 300);
    }
}