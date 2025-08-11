// List of briefs with their dates and descriptions
const briefs = [
    {
        date: '2025-04-07',
        description: 'Executive summary of latest TMT developments and cybersecurity M&A'
      },   
      
    {
        date: '2025-03-31',
        description: 'Latest analysis of TMT sector news and market dynamics'
    },
    {
        date: '2025-03-30',
        description: 'Comprehensive overview of technology and media trends'
    },
    {
        date: '2025-03-29',
        description: 'Key developments in telecommunications and digital transformation'
    },
    {
        date: '2025-03-27',
        description: 'Market insights and strategic analysis for TMT sector'
    },
    {
        date: '2025-03-26',
        description: 'Emerging trends in technology and media landscape'
    },
    {
        date: '2025-03-21',
        description: 'Strategic analysis of TMT market opportunities'
    },
    {
        date: '2025-03-20',
        description: 'Comprehensive review of technology sector developments'
    }
];

// Function to format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Function to create a brief card
function createBriefCard(brief) {
    return `
        <div class="brief-card">
            <h2>Daily Brief</h2>
            <div class="brief-date">${formatDate(brief.date)}</div>
            <p class="brief-description">${brief.description}</p>
            <a href="assets/brief_${brief.date}.pdf" class="download-button" download>
                <i class="fas fa-download"></i>
                Download PDF
            </a>
        </div>
    `;
}

// Function to load briefs
function loadBriefs() {
    const briefsGrid = document.getElementById('briefsGrid');
    if (!briefsGrid) return;

    const briefsHTML = briefs.map(brief => createBriefCard(brief)).join('');
    briefsGrid.innerHTML = briefsHTML;
}

// Load briefs when the page loads
document.addEventListener('DOMContentLoaded', loadBriefs); 