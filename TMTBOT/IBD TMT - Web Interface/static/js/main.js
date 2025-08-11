document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle brief generation
    const generateBtn = document.getElementById('generateBrief');
    const generateStatus = document.getElementById('generateStatus');
    const briefsList = document.getElementById('briefsList');

    generateBtn.addEventListener('click', async function() {
        generateBtn.disabled = true;
        generateStatus.innerHTML = '<div class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></div>Generating new brief...';
        
        try {
            const response = await fetch('/generate_brief', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                generateStatus.innerHTML = '<div class="alert alert-success">Brief generated successfully!</div>';
                updateBriefsList();
                showToast('Success', 'New brief generated successfully!');
            } else {
                generateStatus.innerHTML = '<div class="alert alert-danger">Error generating brief: ' + data.error + '</div>';
                showToast('Error', 'Failed to generate brief');
            }
        } catch (error) {
            generateStatus.innerHTML = '<div class="alert alert-danger">Error: ' + error.message + '</div>';
            showToast('Error', 'Failed to generate brief');
        } finally {
            generateBtn.disabled = false;
        }
    });

    // Function to update the briefs list
    async function updateBriefsList() {
        try {
            const response = await fetch('/list_briefs');
            const data = await response.json();
            
            if (data.success) {
                briefsList.innerHTML = data.briefs.map(brief => `
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <i class="bi bi-file-earmark-pdf text-danger me-2"></i>
                            ${brief}
                        </div>
                        <a href="/download_brief/${brief}" class="btn btn-sm btn-outline-primary">
                            <i class="bi bi-download"></i> Download
                        </a>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error updating briefs list:', error);
        }
    }

    // Function to show toast notifications
    function showToast(title, message) {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="toast-header">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', function () {
            toast.remove();
        });
    }

    // Initial load of briefs list
    updateBriefsList();
}); 