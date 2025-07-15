// TMT Investment Banking Assistant - Main JavaScript

// Global variables
let currentTab = 'briefs';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadBriefs();
    loadInterviewPackages();
    setupTabListeners();
});

// Setup tab change listeners
function setupTabListeners() {
    const briefsTab = document.getElementById('briefs-tab');
    const interviewsTab = document.getElementById('interviews-tab');
    
    briefsTab.addEventListener('click', function() {
        currentTab = 'briefs';
        loadBriefs();
    });
    
    interviewsTab.addEventListener('click', function() {
        currentTab = 'interviews';
        loadInterviewPackages();
    });
}

// Generate TMT Brief
async function generateBrief() {
    showLoading('brief');
    hideMessages();
    
    try {
        const response = await fetch('/generate_brief', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(`Brief generated successfully: ${data.filename}`);
            loadBriefs(); // Refresh the list
        } else {
            showError(data.error || 'Failed to generate brief');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideLoading('brief');
    }
}

// Generate Interview Package
async function generateInterviewPackage() {
    showLoading('interview');
    hideMessages();
    
    try {
        const response = await fetch('/generate_interview_package', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(`Interview package generated successfully: ${data.filename}`);
            loadInterviewPackages(); // Refresh the list
        } else {
            showError(data.error || 'Failed to generate interview package');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideLoading('interview');
    }
}

// Load available briefs
async function loadBriefs() {
    try {
        const response = await fetch('/list_briefs');
        const data = await response.json();
        
        const briefsList = document.getElementById('briefsList');
        
        if (data.success && data.briefs.length > 0) {
            briefsList.innerHTML = data.briefs.map(brief => createBriefCard(brief)).join('');
        } else {
            briefsList.innerHTML = `
                <div class="col-12">
                    <div class="text-center text-muted">
                        <i class="fas fa-newspaper fa-3x mb-3"></i>
                        <p>No briefs available yet. Generate your first TMT brief!</p>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading briefs:', error);
    }
}

// Load available interview packages
async function loadInterviewPackages() {
    try {
        const response = await fetch('/list_interview_packages');
        const data = await response.json();
        
        const packagesList = document.getElementById('interviewPackagesList');
        
        if (data.success && data.packages.length > 0) {
            packagesList.innerHTML = data.packages.map(package => createInterviewPackageCard(package)).join('');
        } else {
            packagesList.innerHTML = `
                <div class="col-12">
                    <div class="text-center text-muted">
                        <i class="fas fa-user-graduate fa-3x mb-3"></i>
                        <p>No interview packages available yet. Generate your first interview package!</p>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading interview packages:', error);
    }
}

// Create brief card HTML
function createBriefCard(filename) {
    const date = extractDateFromFilename(filename);
    const formattedDate = formatDate(date);
    
    return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card content-card fade-in">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <i class="fas fa-file-pdf text-danger me-3 fa-2x"></i>
                        <div>
                            <h6 class="card-title mb-1">TMT Daily Brief</h6>
                            <small class="text-muted">${formattedDate}</small>
                        </div>
                    </div>
                    <p class="card-text">Comprehensive TMT sector analysis with M&A insights, valuations, and market dynamics.</p>
                    <div class="d-grid">
                        <a href="/download_brief/${filename}" class="btn download-btn">
                            <i class="fas fa-download me-2"></i>Download PDF
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Create interview package card HTML
function createInterviewPackageCard(filename) {
    const date = extractDateFromFilename(filename);
    const formattedDate = formatDate(date);
    
    return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card content-card fade-in">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <i class="fas fa-file-alt text-success me-3 fa-2x"></i>
                        <div>
                            <h6 class="card-title mb-1">Interview Package</h6>
                            <small class="text-muted">${formattedDate}</small>
                        </div>
                    </div>
                    <p class="card-text">Complete interview preparation with technical questions, case studies, and behavioral scenarios.</p>
                    <div class="d-grid">
                        <a href="/download_interview_package/${filename}" class="btn download-btn">
                            <i class="fas fa-download me-2"></i>Download Package
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Extract date from filename
function extractDateFromFilename(filename) {
    const match = filename.match(/(\d{4}-\d{2}-\d{2})/);
    return match ? match[1] : '';
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return 'Unknown Date';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Show loading indicator
function showLoading(type) {
    const loadingElement = document.getElementById(`loading${type.charAt(0).toUpperCase() + type.slice(1)}`);
    if (loadingElement) {
        loadingElement.classList.remove('d-none');
    }
}

// Hide loading indicator
function hideLoading(type) {
    const loadingElement = document.getElementById(`loading${type.charAt(0).toUpperCase() + type.slice(1)}`);
    if (loadingElement) {
        loadingElement.classList.add('d-none');
    }
}

// Show success message
function showSuccess(message) {
    const successElement = document.getElementById('successMessage');
    const successText = document.getElementById('successText');
    
    if (successElement && successText) {
        successText.textContent = message;
        successElement.classList.remove('d-none');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            successElement.classList.add('d-none');
        }, 5000);
    }
}

// Show error message
function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    if (errorElement && errorText) {
        errorText.textContent = message;
        errorElement.classList.remove('d-none');
        
        // Auto-hide after 8 seconds
        setTimeout(() => {
            errorElement.classList.add('d-none');
        }, 8000);
    }
}

// Hide all messages
function hideMessages() {
    const successElement = document.getElementById('successMessage');
    const errorElement = document.getElementById('errorMessage');
    
    if (successElement) successElement.classList.add('d-none');
    if (errorElement) errorElement.classList.add('d-none');
}

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to generate brief
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (currentTab === 'briefs') {
            generateBrief();
        } else {
            generateInterviewPackage();
        }
    }
    
    // Escape to hide messages
    if (e.key === 'Escape') {
        hideMessages();
    }
}); 