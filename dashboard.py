"""
Instalily Sales Intelligence Dashboard - Enhanced Version
With powerful features for sales teams
"""
from flask import Flask, render_template_string, jsonify, request, send_file
import sqlite3
import json
from datetime import datetime
import csv
import io

app = Flask(__name__)

# Enhanced HTML Template with New Features
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instalily Sales Intelligence</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
            text-align: center;
        }
        
        .header h1 {
            color: #667eea;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        .action-bar {
            background: white;
            padding: 15px 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .action-btn {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .action-btn:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .action-btn.secondary {
            background: #2ecc71;
        }
        
        .action-btn.secondary:hover {
            background: #27ae60;
        }
        
        .action-btn.tertiary {
            background: #f39c12;
        }
        
        .action-btn.tertiary:hover {
            background: #e67e22;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card .icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-card .label {
            color: #666;
            font-size: 0.9rem;
        }
        
        .filters {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .filter-group {
            flex: 1;
            min-width: 200px;
        }
        
        .filter-group label {
            display: block;
            margin-bottom: 5px;
            color: #666;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .filter-group input,
        .filter-group select {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .filter-group input:focus,
        .filter-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #5568d3;
        }
        
        .contractors {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .view-toggle {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            justify-content: flex-end;
        }
        
        .view-btn {
            padding: 8px 15px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .view-btn.active {
            background: #667eea;
            color: white;
        }
        
        .contractor-card {
            border: 2px solid #f0f0f0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .contractor-card:hover {
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        }
        
        .contractor-card.priority {
            border-left: 5px solid #f39c12;
            background: #fff9f0;
        }
        
        .contractor-card.contacted {
            border-left: 5px solid #2ecc71;
            background: #f0fff4;
        }
        
        .priority-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #f39c12;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .contacted-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #2ecc71;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .contractor-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }
        
        .contractor-name {
            font-size: 1.5rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .rating {
            background: #ffd700;
            color: #333;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .contractor-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .detail-item {
            color: #666;
            font-size: 0.95rem;
        }
        
        .detail-item strong {
            color: #333;
        }
        
        .certifications {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }
        
        .cert-badge {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .insight-box {
            background: #f0f7ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        
        .insight-box h4 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1rem;
        }
        
        .insight-box p {
            color: #444;
            line-height: 1.6;
        }
        
        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .btn-small {
            padding: 8px 15px;
            font-size: 0.9rem;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
        }
        
        .btn-success {
            background: #2ecc71;
            color: white;
        }
        
        .btn-success:hover {
            background: #27ae60;
        }
        
        .btn-warning {
            background: #f39c12;
            color: white;
        }
        
        .btn-warning:hover {
            background: #e67e22;
        }
        
        .btn-secondary {
            background: #95a5a6;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #7f8c8d;
        }
        
        .notes-section {
            margin-top: 15px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
            display: none;
        }
        
        .notes-section.active {
            display: block;
        }
        
        .notes-section textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 0.95rem;
            font-family: inherit;
            resize: vertical;
            min-height: 80px;
        }
        
        .notes-section .saved-notes {
            margin-top: 10px;
            padding: 10px;
            background: white;
            border-radius: 6px;
            font-size: 0.9rem;
            color: #666;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .no-results {
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 1.2rem;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-header h2 {
            color: #333;
        }
        
        .close-modal {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8rem;
            }
            
            .filters {
                flex-direction: column;
            }
            
            .contractor-header {
                flex-direction: column;
            }
            
            .rating {
                margin-top: 10px;
            }
            
            .action-buttons {
                flex-direction: column;
            }
            
            .btn-small {
                width: 100%;
                justify-content: center;
            }
        }
        
        .success-toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #2ecc71;
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            display: none;
            z-index: 2000;
            animation: slideIn 0.3s ease;
        }
        
        .success-toast.active {
            display: block;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Instalily Sales Intelligence Platform</h1>
            <p>AI-Powered Contractor Insights for Roofing Distributors</p>
        </div>
        
        <div class="action-bar">
            <button class="action-btn" onclick="exportToCSV()">
                📊 Export to CSV
            </button>
            <button class="action-btn secondary" onclick="exportPriorities()">
                ⭐ Export Priority Leads
            </button>
            <button class="action-btn tertiary" onclick="showEmailTemplate()">
                📧 Email Template
            </button>
            <button class="action-btn" onclick="generateReport()">
                📄 Generate Report
            </button>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="icon">📋</div>
                <div class="value" id="total-contractors">{{ stats.total }}</div>
                <div class="label">Total Contractors</div>
            </div>
            <div class="stat-card">
                <div class="icon">⭐</div>
                <div class="value">{{ "%.2f"|format(stats.avg_rating) }}/5.0</div>
                <div class="label">Average Rating</div>
            </div>
            <div class="stat-card">
                <div class="icon">🤖</div>
                <div class="value">{{ stats.insights }}</div>
                <div class="label">AI Insights Generated</div>
            </div>
            <div class="stat-card">
                <div class="icon">🎯</div>
                <div class="value" id="priority-count">0</div>
                <div class="label">Priority Leads</div>
            </div>
        </div>
        
        <div class="filters">
            <div class="filter-group">
                <label for="search">🔍 Search Contractors</label>
                <input type="text" id="search" placeholder="Search by name or location...">
            </div>
            <div class="filter-group">
                <label for="min-rating">⭐ Minimum Rating</label>
                <select id="min-rating">
                    <option value="0">All Ratings</option>
                    <option value="3">3.0+</option>
                    <option value="4">4.0+</option>
                    <option value="4.5">4.5+</option>
                    <option value="5">5.0 Only</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="status-filter">📌 Status</label>
                <select id="status-filter">
                    <option value="all">All Contractors</option>
                    <option value="priority">Priority Only</option>
                    <option value="contacted">Contacted</option>
                    <option value="not-contacted">Not Contacted</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="sort">📊 Sort By</label>
                <select id="sort">
                    <option value="rating_desc">Rating (High to Low)</option>
                    <option value="rating_asc">Rating (Low to High)</option>
                    <option value="name_asc">Name (A-Z)</option>
                    <option value="name_desc">Name (Z-A)</option>
                </select>
            </div>
        </div>
        
        <div class="contractors" id="contractors-list">
            <div class="loading">Loading contractors...</div>
        </div>
    </div>
    
    <!-- Email Template Modal -->
    <div id="email-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>📧 Email Template</h2>
                <button class="close-modal" onclick="closeModal('email-modal')">×</button>
            </div>
            <div id="email-template-content"></div>
        </div>
    </div>
    
    <!-- Success Toast -->
    <div id="success-toast" class="success-toast"></div>
    
    <script>
        let allContractors = [];
        let priorityList = new Set(JSON.parse(localStorage.getItem('priorityList') || '[]'));
        let contactedList = new Set(JSON.parse(localStorage.getItem('contactedList') || '[]'));
        let contractorNotes = JSON.parse(localStorage.getItem('contractorNotes') || '{}');
        
        document.addEventListener('DOMContentLoaded', function() {
            loadContractors();
            updatePriorityCount();
            
            // Auto-filter on input
            document.getElementById('search').addEventListener('input', applyFilters);
            document.getElementById('min-rating').addEventListener('change', applyFilters);
            document.getElementById('status-filter').addEventListener('change', applyFilters);
            document.getElementById('sort').addEventListener('change', applyFilters);
        });
        
        async function loadContractors() {
            try {
                const response = await fetch('/api/contractors');
                allContractors = await response.json();
                displayContractors(allContractors);
            } catch (error) {
                document.getElementById('contractors-list').innerHTML = 
                    '<div class="no-results">Error loading contractors</div>';
            }
        }
        
        function applyFilters() {
            const search = document.getElementById('search').value.toLowerCase();
            const minRating = parseFloat(document.getElementById('min-rating').value);
            const statusFilter = document.getElementById('status-filter').value;
            const sort = document.getElementById('sort').value;
            
            let filtered = allContractors.filter(c => {
                const matchesSearch = !search || 
                    c.name.toLowerCase().includes(search) || 
                    (c.address && c.address.toLowerCase().includes(search));
                const matchesRating = c.rating >= minRating;
                
                let matchesStatus = true;
                if (statusFilter === 'priority') matchesStatus = priorityList.has(c.id);
                if (statusFilter === 'contacted') matchesStatus = contactedList.has(c.id);
                if (statusFilter === 'not-contacted') matchesStatus = !contactedList.has(c.id);
                
                return matchesSearch && matchesRating && matchesStatus;
            });
            
            filtered.sort((a, b) => {
                if (sort === 'rating_desc') return b.rating - a.rating;
                if (sort === 'rating_asc') return a.rating - b.rating;
                if (sort === 'name_asc') return a.name.localeCompare(b.name);
                if (sort === 'name_desc') return b.name.localeCompare(a.name);
                return 0;
            });
            
            displayContractors(filtered);
        }
        
        function displayContractors(contractors) {
            const container = document.getElementById('contractors-list');
            
            if (contractors.length === 0) {
                container.innerHTML = '<div class="no-results">No contractors found</div>';
                return;
            }
            
            container.innerHTML = contractors.map(c => {
                const isPriority = priorityList.has(c.id);
                const isContacted = contactedList.has(c.id);
                const notes = contractorNotes[c.id] || '';
                
                return `
                <div class="contractor-card ${isPriority ? 'priority' : ''} ${isContacted ? 'contacted' : ''}" data-id="${c.id}">
                    ${isPriority ? '<span class="priority-badge">⭐ PRIORITY</span>' : ''}
                    ${isContacted ? '<span class="contacted-badge">✓ CONTACTED</span>' : ''}
                    
                    <div class="contractor-header">
                        <div>
                            <div class="contractor-name">${c.name}</div>
                        </div>
                        <div class="rating">⭐ ${c.rating.toFixed(1)}</div>
                    </div>
                    
                    <div class="contractor-details">
                        <div class="detail-item">📍 <strong>Location:</strong> ${c.address || 'N/A'}</div>
                        <div class="detail-item">📞 <strong>Phone:</strong> <a href="tel:${c.phone}">${c.phone || 'N/A'}</a></div>
                        ${c.website ? `<div class="detail-item">🌐 <strong>Website:</strong> <a href="${c.website}" target="_blank">Visit</a></div>` : ''}
                    </div>
                    
                    ${c.certifications && c.certifications.length > 0 ? `
                        <div class="certifications">
                            ${c.certifications.map(cert => `<span class="cert-badge">🏆 ${cert}</span>`).join('')}
                        </div>
                    ` : ''}
                    
                    ${c.insight ? `
                        <div class="insight-box">
                            <h4>🤖 AI Sales Insight</h4>
                            <p>${c.insight}</p>
                        </div>
                    ` : ''}
                    
                    <div class="action-buttons">
                        <button class="btn-small btn-primary" onclick="copyInsight(${c.id})">
                            📋 Copy Insight
                        </button>
                        <button class="btn-small btn-success" onclick="generateEmail(${c.id})">
                            📧 Email Template
                        </button>
                        <button class="btn-small ${isPriority ? 'btn-secondary' : 'btn-warning'}" onclick="togglePriority(${c.id})">
                            ${isPriority ? '★ Remove Priority' : '⭐ Mark Priority'}
                        </button>
                        <button class="btn-small ${isContacted ? 'btn-secondary' : 'btn-success'}" onclick="toggleContacted(${c.id})">
                            ${isContacted ? '✓ Mark Uncontacted' : '📞 Mark Contacted'}
                        </button>
                        <button class="btn-small btn-primary" onclick="toggleNotes(${c.id})">
                            📝 Notes
                        </button>
                    </div>
                    
                    <div id="notes-${c.id}" class="notes-section">
                        <textarea placeholder="Add your notes about this contractor..." onchange="saveNote(${c.id}, this.value)">${notes}</textarea>
                        ${notes ? `<div class="saved-notes"><strong>Saved:</strong> ${notes}</div>` : ''}
                    </div>
                </div>
            `}).join('');
        }
        
        function togglePriority(id) {
            if (priorityList.has(id)) {
                priorityList.delete(id);
            } else {
                priorityList.add(id);
            }
            localStorage.setItem('priorityList', JSON.stringify([...priorityList]));
            updatePriorityCount();
            applyFilters();
            showToast(priorityList.has(id) ? 'Added to priority list!' : 'Removed from priority list');
        }
        
        function toggleContacted(id) {
            if (contactedList.has(id)) {
                contactedList.delete(id);
            } else {
                contactedList.add(id);
            }
            localStorage.setItem('contactedList', JSON.stringify([...contactedList]));
            applyFilters();
            showToast(contactedList.has(id) ? 'Marked as contacted!' : 'Marked as not contacted');
        }
        
        function toggleNotes(id) {
            const notesSection = document.getElementById(`notes-${id}`);
            notesSection.classList.toggle('active');
        }
        
        function saveNote(id, note) {
            contractorNotes[id] = note;
            localStorage.setItem('contractorNotes', JSON.stringify(contractorNotes));
            showToast('Note saved!');
        }
        
        function copyInsight(id) {
            const contractor = allContractors.find(c => c.id === id);
            if (contractor && contractor.insight) {
                navigator.clipboard.writeText(contractor.insight);
                showToast('Insight copied to clipboard!');
            }
        }
        
        function generateEmail(id) {
            const contractor = allContractors.find(c => c.id === id);
            if (!contractor) return;
            
            const emailContent = `
                <h3>Email Template for ${contractor.name}</h3>
                <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Subject:</strong> Premium Roofing Materials Partnership Opportunity</p>
                    <br>
                    <p>Dear ${contractor.name} Team,</p>
                    <br>
                    <p>I hope this email finds you well. I'm reaching out from [Your Company] regarding a potential partnership opportunity.</p>
                    <br>
                    <p><strong>Why we're reaching out:</strong><br>
                    ${contractor.insight || 'Your company has an excellent reputation in the roofing industry.'}</p>
                    <br>
                    <p>We'd love to discuss how our premium materials could support your continued success.</p>
                    <br>
                    <p><strong>Contact Information:</strong><br>
                    Phone: ${contractor.phone}<br>
                    ${contractor.website ? `Website: ${contractor.website}<br>` : ''}
                    Location: ${contractor.address}</p>
                    <br>
                    <p>Would you be available for a brief call this week?</p>
                    <br>
                    <p>Best regards,<br>
                    [Your Name]<br>
                    [Your Company]</p>
                </div>
                <button class="btn-primary" style="padding: 10px 20px; margin-top: 10px;" onclick="copyEmailTemplate()">
                    Copy Email Template
                </button>
            `;
            
            document.getElementById('email-template-content').innerHTML = emailContent;
            document.getElementById('email-modal').classList.add('active');
        }
        
        function copyEmailTemplate() {
            const template = document.getElementById('email-template-content').innerText;
            navigator.clipboard.writeText(template);
            showToast('Email template copied!');
            closeModal('email-modal');
        }
        
        function showEmailTemplate() {
            const priorities = allContractors.filter(c => priorityList.has(c.id));
            if (priorities.length === 0) {
                alert('No priority contractors selected. Mark some contractors as priority first!');
                return;
            }
            generateEmail(priorities[0].id);
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('active');
        }
        
        function updatePriorityCount() {
            document.getElementById('priority-count').textContent = priorityList.size;
        }
        
        function showToast(message) {
            const toast = document.getElementById('success-toast');
            toast.textContent = message;
            toast.classList.add('active');
            setTimeout(() => toast.classList.remove('active'), 3000);
        }
        
        async function exportToCSV() {
            window.location.href = '/export/csv';
            showToast('Downloading CSV...');
        }
        
        async function exportPriorities() {
            const ids = [...priorityList].join(',');
            if (ids) {
                window.location.href = `/export/priorities?ids=${ids}`;
                showToast('Downloading priority leads...');
            } else {
                alert('No priority contractors selected!');
            }
        }
        
        async function generateReport() {
            window.location.href = '/export/report';
            showToast('Generating report...');
        }
    </script>
</body>
</html>
"""

def get_db():
    """Get database connection"""
    return sqlite3.connect('contractors.db')

@app.route('/')
def index():
    """Main dashboard page"""
    conn = get_db()
    cursor = conn.cursor()
    
    stats = {
        'total': cursor.execute('SELECT COUNT(*) FROM contractors').fetchone()[0],
        'avg_rating': cursor.execute('SELECT AVG(rating) FROM contractors WHERE rating > 0').fetchone()[0] or 0,
        'insights': cursor.execute('SELECT COUNT(*) FROM insights').fetchone()[0],
        'high_value': cursor.execute('SELECT COUNT(*) FROM contractors WHERE rating >= 4.5').fetchone()[0]
    }
    
    conn.close()
    
    return render_template_string(HTML_TEMPLATE, stats=stats)

@app.route('/api/contractors')
def api_contractors():
    """API endpoint to get all contractors with insights"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            c.id,
            c.name,
            c.rating,
            c.address,
            c.phone,
            c.website,
            i.insight_text
        FROM contractors c
        LEFT JOIN insights i ON c.id = i.contractor_id
        ORDER BY c.rating DESC, c.name
    ''')
    
    contractors = []
    for row in cursor.fetchall():
        contractor_id, name, rating, address, phone, website, insight = row
        
        cursor.execute('SELECT certification_name FROM certifications WHERE contractor_id = ?', (contractor_id,))
        certs = [r[0] for r in cursor.fetchall()]
        
        contractors.append({
            'id': contractor_id,
            'name': name,
            'rating': rating or 0,
            'address': address,
            'phone': phone,
            'website': website,
            'insight': insight,
            'certifications': certs
        })
    
    conn.close()
    
    return jsonify(contractors)

@app.route('/export/csv')
def export_csv():
    """Export all contractors to CSV"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            c.name,
            c.rating,
            c.address,
            c.phone,
            c.website,
            i.insight_text
        FROM contractors c
        LEFT JOIN insights i ON c.id = i.contractor_id
        ORDER BY c.rating DESC
    ''')
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Contractor Name', 'Rating', 'Location', 'Phone', 'Website', 'AI Insight', 'Certifications'])
    
    # Write data
    for row in cursor.fetchall():
        contractor_id = cursor.execute('SELECT id FROM contractors WHERE name = ?', (row[0],)).fetchone()[0]
        cursor.execute('SELECT certification_name FROM certifications WHERE contractor_id = ?', (contractor_id,))
        certs = ', '.join([r[0] for r in cursor.fetchall()])
        
        writer.writerow([
            row[0],  # name
            row[1],  # rating
            row[2],  # address
            row[3],  # phone
            row[4],  # website
            row[5],  # insight
            certs    # certifications
        ])
    
    conn.close()
    
    # Prepare response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'contractors_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/export/priorities')
def export_priorities():
    """Export priority contractors to CSV"""
    ids = request.args.get('ids', '')
    if not ids:
        return "No priority contractors selected", 400
    
    id_list = [int(i) for i in ids.split(',') if i]
    
    conn = get_db()
    cursor = conn.cursor()
    
    placeholders = ','.join(['?' for _ in id_list])
    cursor.execute(f'''
        SELECT 
            c.name,
            c.rating,
            c.address,
            c.phone,
            c.website,
            i.insight_text
        FROM contractors c
        LEFT JOIN insights i ON c.id = i.contractor_id
        WHERE c.id IN ({placeholders})
        ORDER BY c.rating DESC
    ''', id_list)
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Contractor Name', 'Rating', 'Location', 'Phone', 'Website', 'AI Insight', 'Certifications'])
    
    for row in cursor.fetchall():
        contractor_id = cursor.execute('SELECT id FROM contractors WHERE name = ?', (row[0],)).fetchone()[0]
        cursor.execute('SELECT certification_name FROM certifications WHERE contractor_id = ?', (contractor_id,))
        certs = ', '.join([r[0] for r in cursor.fetchall()])
        
        writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], certs])
    
    conn.close()
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'priority_leads_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/export/report')
def export_report():
    """Generate a summary report"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get statistics
    stats = {
        'total': cursor.execute('SELECT COUNT(*) FROM contractors').fetchone()[0],
        'avg_rating': cursor.execute('SELECT AVG(rating) FROM contractors WHERE rating > 0').fetchone()[0],
        'high_rated': cursor.execute('SELECT COUNT(*) FROM contractors WHERE rating >= 4.5').fetchone()[0],
        'with_insights': cursor.execute('SELECT COUNT(*) FROM insights').fetchone()[0],
    }
    
    # Get top contractors
    cursor.execute('''
        SELECT c.name, c.rating, c.address, i.insight_text
        FROM contractors c
        LEFT JOIN insights i ON c.id = i.contractor_id
        WHERE c.rating >= 4.5
        ORDER BY c.rating DESC
        LIMIT 10
    ''')
    top_contractors = cursor.fetchall()
    
    conn.close()
    
    # Generate report
    report = f"""
INSTALILY SALES INTELLIGENCE REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*80}

SUMMARY STATISTICS:
-------------------
Total Contractors: {stats['total']}
Average Rating: {stats['avg_rating']:.2f}/5.0
High-Rated Contractors (≥4.5): {stats['high_rated']}
AI Insights Generated: {stats['with_insights']}

TOP 10 HIGH-VALUE LEADS:
-------------------------
"""
    
    for idx, (name, rating, address, insight) in enumerate(top_contractors, 1):
        report += f"\n{idx}. {name}\n"
        report += f"   Rating: {rating}/5.0\n"
        report += f"   Location: {address}\n"
        report += f"   AI Insight: {insight or 'N/A'}\n"
        report += "-" * 80 + "\n"
    
    report += f"\n{'='*80}\n"
    report += "Report generated by Instalily Sales Intelligence Platform\n"
    
    # Return as text file
    return send_file(
        io.BytesIO(report.encode('utf-8')),
        mimetype='text/plain',
        as_attachment=True,
        download_name=f'sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    )

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🏠 INSTALILY SALES INTELLIGENCE DASHBOARD - ENHANCED")
    print("="*80)
    print("\n✨ New Features:")
    print("  • Mark contractors as Priority")
    print("  • Track contacted contractors")
    print("  • Add private notes")
    print("  • Export to CSV")
    print("  • Generate email templates")
    print("  • Download reports")
    print("\nStarting server...")
    print("Dashboard URL: http://127.0.0.1:8080")
    print("\nPress Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8080)