// ==================== Configuration ====================
const API_BASE_URL = 'http://localhost:5000';

// ==================== DOM Elements ====================
const textForm = document.getElementById('textForm');
const imageForm = document.getElementById('imageForm');
const claimInput = document.getElementById('claimInput');
const imageInput = document.getElementById('imageInput');
const textResults = document.getElementById('textResults');
const imageResults = document.getElementById('imageResults');
const tabBtns = document.querySelectorAll('.tab-btn');

// ==================== Event Listeners ====================

// Tab switching
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;
        switchTab(tabId);
    });
});

// Text verification form
textForm.addEventListener('submit', (e) => {
    e.preventDefault();
    verifyText();
});

// Image verification form
imageForm.addEventListener('submit', (e) => {
    e.preventDefault();
    verifyImage();
});

// ==================== Functions ====================

function switchTab(tabId) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from buttons
    tabBtns.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

async function verifyText() {
    const claim = claimInput.value.trim();
    
    if (!claim) {
        alert('Please enter a claim to verify');
        return;
    }
    
    textResults.classList.remove('hidden');
    textResults.innerHTML = '<div class="loading"></div> Analyzing claim...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/verify-text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim })
        });
        
        if (!response.ok) throw new Error('Request failed');
        const data = await response.json();
        
        displayTextResults(data);
    } catch (error) {
        textResults.innerHTML = `<div class="result-error">Error: ${error.message}</div>`;
    }
}

async function verifyImage() {
    const file = imageInput.files[0];
    
    if (!file) {
        alert('Please select an image');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = async (e) => {
        imageResults.classList.remove('hidden');
        imageResults.innerHTML = '<div class="loading"></div> Analyzing image...';
        
        try {
            const response = await fetch(`${API_BASE_URL}/verify-image`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: e.target.result })
            });
            
            if (!response.ok) throw new Error('Request failed');
            const data = await response.json();
            
            displayImageResults(data);
        } catch (error) {
            imageResults.innerHTML = `<div class="result-error">Error: ${error.message}</div>`;
        }
    };
    reader.readAsDataURL(file);
}

function displayTextResults(data) {
    const verdictClass = data.verdict.toLowerCase();
    const confidence = (data.confidence * 100).toFixed(1);
    
    textResults.innerHTML = `
        <div class="result-item">
            <div class="result-label">Claim:</div>
            <div class="result-value">${escapeHtml(data.claim)}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Verdict:</div>
            <span class="verdict ${verdictClass}">${data.verdict}</span>
        </div>
        <div class="result-item">
            <div class="result-label">Confidence Score:</div>
            <div class="result-value">${confidence}%</div>
        </div>
        <div class="result-item">
            <div class="result-label">Verification Details:</div>
            <div class="result-value">
                <strong>News Agencies Used:</strong> ${data.news_agencies.total_count} (${data.news_agencies.tier_1_count} Tier-1)
            </div>
        </div>
        <div class="result-item">
            <div class="result-label">Encoding (One-Hot):</div>
            <div class="result-value">
                TRUE: ${data.encoded_verdict.true.toFixed(2)} | 
                FALSE: ${data.encoded_verdict.false.toFixed(2)} | 
                MIXED: ${data.encoded_verdict.mixed.toFixed(2)}
            </div>
        </div>
    `;
}

function displayImageResults(data) {
    if (data.image_features.error) {
        imageResults.innerHTML = `<div class="result-error">Error: ${data.image_features.error}</div>`;
        return;
    }
    
    imageResults.innerHTML = `
        <div class="result-item">
            <div class="result-label">Image Quality Assessment:</div>
            <span class="verdict ${data.quality_assessment.toLowerCase()}">${data.quality_assessment}</span>
        </div>
        <div class="result-item">
            <div class="result-label">Edge Density:</div>
            <div class="result-value">${data.image_features.edge_density.toFixed(4)}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Contrast Score:</div>
            <div class="result-value">${data.image_features.contrast.toFixed(2)}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Quality Score:</div>
            <div class="result-value">${data.image_features.quality_score.toFixed(4)}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Image Dimensions:</div>
            <div class="result-value">${data.image_shape.join(' x ')}</div>
        </div>
    `;
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ==================== Initialize ====================
console.log('🚀 News Verification AI Frontend loaded');
console.log(`API Base URL: ${API_BASE_URL}`);
