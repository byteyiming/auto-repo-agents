// DOCU-GEN Web Application JavaScript - Mobile First
const form = document.getElementById('generateForm');
const statusDiv = document.getElementById('status');
const progressDiv = document.getElementById('progress');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const resultsDiv = document.getElementById('results');
const resultsContainer = document.getElementById('resultsContainer');
const generateBtn = document.getElementById('generateBtn');
const previewModal = document.getElementById('previewModal');
const previewContent = document.getElementById('previewContent');
const closePreviewBtn = document.getElementById('closePreview');
const wsStatus = document.getElementById('wsStatus');
const wsIndicator = document.getElementById('wsIndicator');
const wsStatusText = document.getElementById('wsStatusText');
const errorDetails = document.getElementById('errorDetails');
const errorDetailsContent = document.getElementById('errorDetailsContent');
const errorDetailsText = document.getElementById('errorDetailsText');
const errorDetailsToggle = document.getElementById('errorDetailsToggle');
const downloadAllBtn = document.getElementById('downloadAllBtn');

let projectId = null;
let websocket = null;
let reconnectAttempts = 0;
let pollInterval = null;
let wsConnected = false;
let isPolling = false;
const maxReconnectAttempts = 5;
let allDocuments = []; // Store all documents for download all

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userIdea = document.getElementById('userIdea').value.trim();
    const profile = document.querySelector('input[name="profile"]:checked').value;
    
    if (!userIdea) {
        showStatus('Please enter a project idea', 'error');
        return;
    }
    
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';
    generateBtn.classList.add('loading');
    showStatus('Starting documentation generation...', 'info');
    hideErrorDetails();
    progressDiv.classList.remove('hidden');
    resultsDiv.classList.add('hidden');
    downloadAllBtn.classList.add('hidden');
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    allDocuments = []; // Clear previous documents
    
    // Scroll to progress
    progressDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_idea: userIdea, profile: profile})
            // Note: phase1_only removed - workflow now pauses after Phase 1 for approval

        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        projectId = data.project_id;
        connectWebSocket(projectId);
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
        showErrorDetails('Generation start failed', error.message);
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Documentation';
        generateBtn.classList.remove('loading');
        progressDiv.classList.add('hidden');
        updateWebSocketStatus(false, false);
    }
});

// Update WebSocket status indicator
function updateWebSocketStatus(connected, polling = false) {
    wsConnected = connected;
    isPolling = polling;
    wsStatus.classList.remove('hidden');
    
    if (connected && !polling) {
        wsIndicator.className = 'w-2 h-2 rounded-full bg-green-500 animate-pulse';
        wsStatusText.textContent = 'Connected (WebSocket)';
        wsStatusText.className = 'text-xs text-green-600';
    } else if (polling) {
        wsIndicator.className = 'w-2 h-2 rounded-full bg-yellow-500';
        wsStatusText.textContent = 'Polling (Fallback)';
        wsStatusText.className = 'text-xs text-yellow-600';
    } else {
        wsIndicator.className = 'w-2 h-2 rounded-full bg-gray-400';
        wsStatusText.textContent = 'Disconnected';
        wsStatusText.className = 'text-xs text-gray-500';
    }
}

// WebSocket connection
function connectWebSocket(projectId) {
    if (websocket) websocket.close();
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    websocket = new WebSocket(`${protocol}//${window.location.host}/ws/${projectId}`);
    reconnectAttempts = 0;
    updateWebSocketStatus(false, false);
    
    websocket.onopen = () => {
        updateWebSocketStatus(true, false);
        showStatus('Connected. Generating documentation...', 'info');
    };
    websocket.onmessage = (event) => {
        try {
            handleWebSocketMessage(JSON.parse(event.data));
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    };
    websocket.onerror = () => {
        updateWebSocketStatus(false, false);
        showStatus('Connection error. Using fallback...', 'error');
        fallbackToPolling(projectId);
    };
    websocket.onclose = () => {
        updateWebSocketStatus(false, false);
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            setTimeout(() => connectWebSocket(projectId), 1000 * reconnectAttempts);
        } else {
            fallbackToPolling(projectId);
        }
    };
}

// Handle WebSocket messages
function handleWebSocketMessage(message) {
    switch (message.type) {
        case 'connected':
            // WebSocket connection confirmed
            updateWebSocketStatus(true, false);
            showStatus('Connected. Waiting for updates...', 'info');
            break;
        case 'heartbeat':
            // Heartbeat message - just keep connection alive, no UI update needed
            break;
        case 'start':
            updateProgress(5);
            showStatus('Generation started...', 'info');
            break;
        case 'phase':
            if (message.phase === 'phase_1') {
                updateProgress(25);
                showStatus('Phase 1: Foundational documents...', 'info');
            } else if (message.phase === 'phase_2') {
                updateProgress(60);
                showStatus('Phase 2: Parallel generation...', 'info');
            } else if (message.phase === 'phase_3') {
                updateProgress(85);
                showStatus('Phase 3: Finalization...', 'info');
            }
            break;
        case 'progress':
            updateProgress(message.progress || 0);
            if (message.message) {
                showStatus(message.message, 'info');
            }
            break;
        case 'phase_1':
            // Phase 1 document complete - show review UI for this specific document
            if (message.status === 'complete' || message.status === 'awaiting_approval') {
                const docName = message.document || message.task_id || 'Document';
                // Use agent_type from message if available, otherwise fall back to task_id mapping
                const agentType = message.agent_type || (message.task_id ? mapTaskIdToAgentType(message.task_id) : null);
                showDocumentReview(docName, message.task_id, agentType);
            }
            break;
        case 'document_approved':
            // Document approved - hide review UI and continue
            // Note: Button states are already reset in approvePhase1() after API success
            // This is just a confirmation message
            if (currentReviewingAgentType === message.agent_type) {
                // Only hide if this is the document we just approved
                hideDocumentReview();
            }
            showStatus(`Document ${message.agent_type || 'document'} approved! Continuing...`, 'success');
            break;
        case 'document_rejected':
            // Document rejected - hide review UI and show error
            hideDocumentReview();
            showStatus(`Document ${message.agent_type || 'document'} rejected. Workflow stopped.`, 'error');
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Documentation';
            generateBtn.classList.remove('loading');
            progressDiv.classList.add('hidden');
            break;
        case 'phase1_approved':
            // Phase 1 approved - hide review UI and continue (legacy)
            hideDocumentReview();
            showStatus('Phase 1 approved! Continuing with Phase 2+...', 'success');
            updateProgress(30);
            break;
        case 'phase1_rejected':
            // Phase 1 rejected - hide review UI and show error (legacy)
            hideDocumentReview();
            showStatus('Phase 1 rejected. Workflow stopped.', 'error');
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Documentation';
            generateBtn.classList.remove('loading');
            progressDiv.classList.add('hidden');
            break;
        case 'complete':
            updateProgress(100);
            showStatus('Documentation generated successfully!', 'success');
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Documentation';
            generateBtn.classList.remove('loading');
            progressDiv.classList.add('hidden');
            hideDocumentReview(); // Hide document review if still visible
            if (websocket) {
                websocket.close();
                websocket = null;
            }
            fetchResults();
            // Scroll to results
            setTimeout(() => {
                resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 300);
            break;
        case 'error':
            const errorMsg = message.message || 'Unknown error';
            showStatus('Error: ' + errorMsg, 'error');
            showErrorDetails(errorMsg, message.error || message.details || null);
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Documentation';
            generateBtn.classList.remove('loading');
            progressDiv.classList.add('hidden');
            if (websocket) {
                websocket.close();
                websocket = null;
            }
            updateWebSocketStatus(false, false);
            break;
    }
}

// Update progress bar
function updateProgress(percent) {
    progressBar.style.width = percent + '%';
    progressText.textContent = Math.round(percent) + '%';
}

// Show status message
function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = `mb-4 px-4 py-3 rounded-lg text-sm ${
        type === 'error' ? 'bg-red-50 text-red-700 border border-red-200' :
        type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' :
        'bg-blue-50 text-blue-700 border border-blue-200'
    }`;
    statusDiv.classList.remove('hidden');
}

// Show error details
function showErrorDetails(message, details) {
    if (message || details) {
        errorDetails.classList.remove('hidden');
        let errorText = message || 'Unknown error';
        if (details) {
            if (typeof details === 'string') {
                errorText += '\n\nDetails: ' + details;
            } else {
                errorText += '\n\nDetails: ' + JSON.stringify(details, null, 2);
            }
        }
        errorDetailsText.textContent = errorText;
    } else {
        errorDetails.classList.add('hidden');
    }
}

// Toggle error details
function toggleErrorDetails() {
    const isHidden = errorDetailsContent.classList.contains('hidden');
    if (isHidden) {
        errorDetailsContent.classList.remove('hidden');
        errorDetailsToggle.textContent = '▲';
    } else {
        errorDetailsContent.classList.add('hidden');
        errorDetailsToggle.textContent = '▼';
    }
}
window.toggleErrorDetails = toggleErrorDetails; // Make it global

// Hide error details
function hideErrorDetails() {
    errorDetails.classList.add('hidden');
    errorDetailsContent.classList.add('hidden');
    errorDetailsToggle.textContent = '▼';
}

// Fallback to polling
function fallbackToPolling(projectId) {
    updateWebSocketStatus(false, true);
    showStatus('WebSocket unavailable. Using automatic refresh...', 'info');
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(() => checkStatus(projectId), 2000);
    checkStatus(projectId);
}

// Check status (polling fallback)
async function checkStatus(projectId) {
    if (!projectId) return;
    try {
        const response = await fetch(`/api/status/${projectId}`);
        const data = await response.json();
        const completed = data.completed_agents?.length || 0;
        const total = 15;
        const percent = Math.round((completed / total) * 100);
        updateProgress(percent);
        if (data.status === 'complete') {
            if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
            }
            showStatus('Documentation generated successfully!', 'success');
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Documentation';
            generateBtn.classList.remove('loading');
            progressDiv.classList.add('hidden');
            await fetchResults();
            setTimeout(() => {
                resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 300);
        } else if (data.status === 'failed') {
            if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
            }
            const errorMsg = data.error || 'Generation failed. Please try again.';
            showStatus('Generation failed: ' + errorMsg, 'error');
            showErrorDetails(errorMsg, data.error_details || null);
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Documentation';
            generateBtn.classList.remove('loading');
            progressDiv.classList.add('hidden');
            updateWebSocketStatus(false, false);
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// Fetch and display results
async function fetchResults() {
    try {
        const response = await fetch(`/api/results/${projectId}`);
        const data = await response.json();
        
        resultsContainer.innerHTML = '';
        const documentsByLevel = data.documents_by_level || {};
        
        // Collect all documents for download all
        allDocuments = [];
        
        const levels = [
            { key: 'level_1_strategic', title: 'Strategic Documents', icon: '🎯', color: 'red' },
            { key: 'level_2_product', title: 'Product Documents', icon: '📊', color: 'blue' },
            { key: 'level_3_technical', title: 'Technical Documents', icon: '💻', color: 'green' },
            { key: 'cross_level', title: 'Cross-Level Documents', icon: '🌐', color: 'gray' }
        ];
        
        levels.forEach(level => {
            const levelData = documentsByLevel[level.key];
            if (levelData && levelData.documents && levelData.documents.length > 0) {
                const section = createLevelSection(level, levelData);
                resultsContainer.appendChild(section);
                // Collect documents for download all
                levelData.documents.forEach(doc => {
                    allDocuments.push({
                        type: doc.type,
                        display_name: doc.display_name,
                        file_path: doc.file_path
                    });
                });
            }
        });
        
        if (resultsContainer.children.length === 0) {
            resultsContainer.innerHTML = '<p class="text-gray-500 text-center py-8">No documents found</p>';
            downloadAllBtn.classList.add('hidden');
        } else {
            // Show download all button if documents are available
            downloadAllBtn.classList.remove('hidden');
        }
        
        // Hide error details on success
        hideErrorDetails();
        
        resultsDiv.classList.remove('hidden');
    } catch (error) {
        console.error('Error fetching results:', error);
        showStatus('Error loading results: ' + error.message, 'error');
        showErrorDetails('Error loading results', error.message);
    }
}

// Create level section
function createLevelSection(level, levelData) {
    const section = document.createElement('div');
    section.className = 'border border-gray-200 rounded-lg p-4';
    
    const title = document.createElement('h3');
    title.className = 'text-base font-semibold text-gray-900 mb-3 flex items-center gap-2';
    title.innerHTML = `<span>${level.icon}</span> <span>${level.title}</span>`;
    section.appendChild(title);
    
    const list = document.createElement('div');
    list.className = 'space-y-2';
    
    levelData.documents.forEach((doc, index) => {
        const item = document.createElement('div');
        item.className = 'doc-item flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 border border-gray-200 rounded-lg bg-gray-50 hover:bg-white hover:shadow-sm transition-all';
        
        const name = document.createElement('div');
        name.className = 'flex-1 min-w-0';
        const nameText = document.createElement('span');
        nameText.className = 'text-sm font-medium text-gray-900 block truncate';
        nameText.textContent = doc.display_name;
        name.appendChild(nameText);
        if (doc.file_size_human) {
            const size = document.createElement('span');
            size.className = 'text-xs text-gray-500 mt-1 block';
            size.textContent = doc.file_size_human;
            name.appendChild(size);
        }
        item.appendChild(name);
        
        const actions = document.createElement('div');
        actions.className = 'flex gap-2 shrink-0';
        
        const previewBtn = document.createElement('button');
        previewBtn.className = 'px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 hover:border-blue-300 transition-colors';
        previewBtn.textContent = 'Preview';
        previewBtn.onclick = () => previewDocument(doc);
        actions.appendChild(previewBtn);
        
        const downloadBtn = document.createElement('a');
        downloadBtn.href = `/api/download/${projectId}/${doc.type}`;
        downloadBtn.className = 'px-3 py-1.5 text-xs font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center justify-center';
        downloadBtn.textContent = 'Download';
        downloadBtn.download = doc.display_name;
        actions.appendChild(downloadBtn);
        
        item.appendChild(actions);
        list.appendChild(item);
    });
    
    section.appendChild(list);
    return section;
}

// Preview document
async function previewDocument(doc) {
    // Prevent multiple simultaneous requests
    if (previewModal.dataset.loading === 'true') {
        return;
    }
    
    try {
        previewModal.dataset.loading = 'true';
        previewModal.classList.remove('hidden');
        previewContent.innerHTML = '<div class="text-center py-8"><div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div><p class="mt-4 text-gray-500">Loading preview...</p></div>';
        
        let text;
        
        // If content is provided directly, use it (for Phase 1 documents)
        if (doc.content) {
            text = doc.content;
        } else {
            // Otherwise, fetch from API
            const response = await fetch(`/api/preview/${projectId}/${doc.type}`);
            if (!response.ok) {
                const errorText = await response.text().catch(() => 'Failed to fetch');
                throw new Error(errorText || 'Failed to fetch');
            }
            text = await response.text();
        }
        
        // Render markdown
        if (typeof marked !== 'undefined') {
            previewContent.innerHTML = marked.parse(text);
        } else {
            previewContent.textContent = text;
        }
    } catch (error) {
        console.error('Error previewing:', error);
        previewContent.innerHTML = `<div class="text-center py-8 text-red-600"><p>Error loading preview: ${error.message}</p></div>`;
    } finally {
        previewModal.dataset.loading = 'false';
    }
}

// Close preview modal
closePreviewBtn.addEventListener('click', () => {
    previewModal.classList.add('hidden');
});

// Close modal on background click
previewModal.addEventListener('click', (e) => {
    if (e.target === previewModal) {
        previewModal.classList.add('hidden');
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !previewModal.classList.contains('hidden')) {
        previewModal.classList.add('hidden');
    }
});

// Download all documents as ZIP
async function downloadAllDocuments() {
    if (!projectId || allDocuments.length === 0) {
        showStatus('No documents available for download', 'error');
        return;
    }
    
    try {
        downloadAllBtn.disabled = true;
        downloadAllBtn.textContent = '📦 Downloading...';
        
        // Call API to generate ZIP
        const response = await fetch(`/api/download-all/${projectId}`, {
            method: 'GET'
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate ZIP file');
        }
        
        // Get blob and create download link
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `docu-gen-${projectId}-${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showStatus('All documents downloaded successfully!', 'success');
    } catch (error) {
        console.error('Error downloading all documents:', error);
        showStatus('Error downloading all documents: ' + error.message, 'error');
        showErrorDetails('Download error', error.message);
    } finally {
        downloadAllBtn.disabled = false;
        downloadAllBtn.textContent = '📦 Download All';
    }
}
window.downloadAllDocuments = downloadAllDocuments; // Make it global

// Document Review Functions (per-document approval)
let currentReviewingDocument = null;
let currentReviewingAgentType = null;

// Helper function to map task_id to agent_type (fallback)
// Refresh the previous documents list to show newly approved documents
async function refreshPreviousDocumentsList() {
    if (!projectId) return;
    
    const previousDocumentsSection = document.getElementById('previousDocumentsSection');
    const previousDocumentsList = document.getElementById('previousDocumentsList');
    
    if (!previousDocumentsSection || !previousDocumentsList) return;
    
    try {
        const prevDocsResponse = await fetch(`/api/phase1-documents-list/${projectId}`);
        if (prevDocsResponse.ok) {
            const prevDocsData = await prevDocsResponse.json();
            // Show all approved documents
            const previousDocs = prevDocsData.documents.filter(doc => doc.status === 'approved');
            
            if (previousDocs.length > 0) {
                previousDocumentsList.innerHTML = '';
                previousDocs.forEach(doc => {
                    const docItem = createPreviousDocumentItem(doc);
                    previousDocumentsList.appendChild(docItem);
                });
                previousDocumentsSection.classList.remove('hidden');
            } else {
                previousDocumentsSection.classList.add('hidden');
            }
        }
    } catch (error) {
        console.debug('Error refreshing previous documents:', error);
    }
}

function mapTaskIdToAgentType(taskId) {
const taskToAgentType = {
        'requirements': 'requirements_analyst',
        'project_charter': 'project_charter',
        'user_stories': 'user_stories',
        'business_model': 'business_model',
        'marketing_plan': 'marketing_plan',
        'pm_doc': 'pm_documentation',
        'stakeholder_doc': 'stakeholder_communication',
        'wbs': 'wbs_agent',
        'technical_doc': 'technical_documentation'
    };
    return taskToAgentType[taskId] || taskId;
}

async function showDocumentReview(docName, taskId, agentType = null) {
    if (!projectId) {
        console.error('No project ID available for document review');
        return;
    }
    
    // Use provided agent_type or map from task_id
    const finalAgentType = agentType || mapTaskIdToAgentType(taskId);
    currentReviewingAgentType = finalAgentType;
    currentReviewingDocument = docName;
    
    const phase1Review = document.getElementById('phase1Review');
    const phase1Documents = document.getElementById('phase1Documents');
    const previousDocumentsSection = document.getElementById('previousDocumentsSection');
    const previousDocumentsList = document.getElementById('previousDocumentsList');
    
    try {
        // Fetch previously generated documents
        try {
            const prevDocsResponse = await fetch(`/api/phase1-documents-list/${projectId}`);
            if (prevDocsResponse.ok) {
                const prevDocsData = await prevDocsResponse.json();
                const previousDocs = prevDocsData.documents.filter(doc => 
                    doc.agent_type !== finalAgentType && doc.status === 'approved'
                );
                
                if (previousDocs.length > 0) {
                    previousDocumentsList.innerHTML = '';
                    previousDocs.forEach(doc => {
                        const docItem = createPreviousDocumentItem(doc);
                        previousDocumentsList.appendChild(docItem);
                    });
                    previousDocumentsSection.classList.remove('hidden');
                } else {
                    previousDocumentsSection.classList.add('hidden');
                }
            }
        } catch (error) {
            console.debug('Error loading previous documents:', error);
            previousDocumentsSection.classList.add('hidden');
        }
        
        // Fetch the specific document
        const response = await fetch(`/api/document/${projectId}/${finalAgentType}`);
        if (!response.ok) {
            throw new Error('Failed to fetch document');
        }
        
        const data = await response.json();
        phase1Documents.innerHTML = '';
        
        // Display the document
        const docCard = createDocumentCard(docName, data);
        phase1Documents.appendChild(docCard);
        
        // Update title
        const titleElement = phase1Review.querySelector('h3');
        if (titleElement) {
            titleElement.textContent = `Review: ${docName}`;
        }
        
        // Update description
        const descElement = document.getElementById('reviewDocumentDescription');
        if (descElement) {
            descElement.textContent = `${docName} has been generated and is ready for your review. Please review it below and approve to continue with the next document.`;
        }
        
        // Ensure button states are reset before showing review UI
        const approveBtn = document.getElementById('approvePhase1Btn');
        const rejectBtn = document.getElementById('rejectPhase1Btn');
        if (approveBtn) {
            approveBtn.disabled = false;
            approveBtn.textContent = '✅ Approve & Continue';
        }
        if (rejectBtn) {
            rejectBtn.disabled = false;
            rejectBtn.textContent = '❌ Reject & Stop';
        }
        
        // Reset approval flag
        isApproving = false;
        
        // Show review UI
        phase1Review.classList.remove('hidden');
        phase1Review.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Show notes section
        const notesSection = document.getElementById('approvalNotes');
        if (notesSection) {
            notesSection.classList.remove('hidden');
        }
        
        showStatus(`${docName} generated! Please review and approve to continue.`, 'info');
        
        // Focus on notes textarea for better UX
        const notesText = document.getElementById('approvalNotesText');
        if (notesText) {
            setTimeout(() => notesText.focus(), 100);
        }
    } catch (error) {
        console.error('Error loading document:', error);
        showStatus('Error loading document: ' + error.message, 'error');
    }
}

function createPreviousDocumentItem(doc) {
    const item = document.createElement('div');
    item.className = 'flex items-center justify-between p-2 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors';
    
    const left = document.createElement('div');
    left.className = 'flex items-center gap-2 flex-1';
    
    const icon = document.createElement('span');
    icon.textContent = '✅';
    icon.className = 'text-sm';
    left.appendChild(icon);
    
    const name = document.createElement('span');
    name.textContent = doc.display_name;
    name.className = 'text-sm font-medium text-gray-700';
    left.appendChild(name);
    
    if (doc.quality_score) {
        const score = document.createElement('span');
        score.textContent = `Quality: ${Math.round(doc.quality_score)}%`;
        score.className = 'text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full';
        left.appendChild(score);
    }
    
    item.appendChild(left);
    
    const previewBtn = document.createElement('button');
    previewBtn.textContent = 'Preview';
    previewBtn.className = 'px-3 py-1 text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors';
    previewBtn.onclick = async () => {
        try {
            const response = await fetch(`/api/document/${projectId}/${doc.agent_type}`);
            if (response.ok) {
                const docData = await response.json();
                previewDocument({
                    type: doc.agent_type,
                    display_name: doc.display_name,
                    content: docData.content
                });
            }
        } catch (error) {
            console.error('Error previewing previous document:', error);
            showStatus('Error previewing document: ' + error.message, 'error');
        }
    };
    item.appendChild(previewBtn);
    
    return item;
}

function createDocumentCard(docName, docData) {
    const card = document.createElement('div');
    card.className = 'border border-gray-200 rounded-lg p-4 bg-gray-50';
    
    const header = document.createElement('div');
    header.className = 'flex items-center justify-between mb-3';
    
    const title = document.createElement('h4');
    title.className = 'text-base font-semibold text-gray-900';
    title.textContent = docName;
    header.appendChild(title);
    
    const info = document.createElement('div');
    info.className = 'flex items-center gap-3';
    
    if (docData.version) {
        const version = document.createElement('span');
        version.className = 'text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-medium';
        version.textContent = `Version ${docData.version}`;
        info.appendChild(version);
    }
    
    if (docData.quality_score) {
        const score = document.createElement('span');
        score.className = 'text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full font-medium';
        score.textContent = `Quality: ${Math.round(docData.quality_score)}%`;
        info.appendChild(score);
    }
    
    header.appendChild(info);
    card.appendChild(header);
    
    // Preview button
    const previewBtn = document.createElement('button');
    previewBtn.className = 'w-full mt-2 px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 hover:border-blue-300 transition-colors';
    previewBtn.textContent = '📄 Preview Document';
    previewBtn.onclick = () => {
        previewDocument({
            type: currentReviewingAgentType,
            display_name: docName,
            content: docData.content
        });
    };
    card.appendChild(previewBtn);
    
    return card;
}

function hideDocumentReview() {
    const phase1Review = document.getElementById('phase1Review');
    if (phase1Review) {
        phase1Review.classList.add('hidden');
    }
    
    // Clear notes
    const notesText = document.getElementById('approvalNotesText');
    if (notesText) {
        notesText.value = '';
    }
    
    // Reset button states
    const approveBtn = document.getElementById('approvePhase1Btn');
    const rejectBtn = document.getElementById('rejectPhase1Btn');
    if (approveBtn) {
        approveBtn.disabled = false;
        approveBtn.textContent = '✅ Approve & Continue';
    }
    if (rejectBtn) {
        rejectBtn.disabled = false;
        rejectBtn.textContent = '❌ Reject & Stop';
    }
    
    // Reset approval flag
    isApproving = false;
    
    currentReviewingDocument = null;
    currentReviewingAgentType = null;
}

// Legacy function for backward compatibility
async function showPhase1Review() {
    // This is now handled by showDocumentReview for individual documents
    // But we keep it for any legacy calls
    if (currentReviewingDocument) {
        await showDocumentReview(currentReviewingDocument, currentReviewingAgentType || 'requirements');
    }
}

function hidePhase1Review() {
    hideDocumentReview();
}

// Track if approval is in progress to prevent duplicate requests
let isApproving = false;

async function approvePhase1() {
    if (!projectId || !currentReviewingAgentType) {
        showStatus('No document available for approval', 'error');
        return;
    }
    
    // Prevent duplicate approval requests
    if (isApproving) {
        console.log('Approval already in progress, ignoring duplicate request');
        return;
    }
    
    const approveBtn = document.getElementById('approvePhase1Btn');
    const rejectBtn = document.getElementById('rejectPhase1Btn');
    const notesText = document.getElementById('approvalNotesText');
    
    // Check if buttons exist
    if (!approveBtn || !rejectBtn) {
        console.error('Approval buttons not found');
        return;
    }
    
    // Prevent duplicate clicks
    if (approveBtn.disabled) {
        console.log('Button already disabled, approval in progress');
        return;
    }
    
    // Set approval in progress flag
    isApproving = true;
    
    // Disable buttons
    approveBtn.disabled = true;
    rejectBtn.disabled = true;
    approveBtn.textContent = 'Approving...';
    
    try {
        const notes = notesText ? notesText.value.trim() || null : null;
        console.log(`Approving document: ${currentReviewingAgentType} for project: ${projectId}`);
        
        const response = await fetch(`/api/approve-document/${projectId}/${currentReviewingAgentType}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes: notes })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Document approved successfully:', data);
        
        showStatus(`${currentReviewingDocument || 'Document'} approved! Workflow will continue...`, 'success');
        
        // Update progress
        updateProgress(30);
        
        // Refresh the previous documents list to show the newly approved document
        await refreshPreviousDocumentsList();
        
        // Hide review UI and reset button states
        hideDocumentReview();
        
        // Reset approval flag
        isApproving = false;
        
        // Note: The workflow will continue automatically after approval
        // The next document will be generated and shown via WebSocket message
    } catch (error) {
        console.error('Error approving document:', error);
        showStatus('Error approving document: ' + error.message, 'error');
        
        // Reset approval flag on error
        isApproving = false;
        
        // Reset button states on error
        if (approveBtn) {
            approveBtn.disabled = false;
            approveBtn.textContent = '✅ Approve & Continue';
        }
        if (rejectBtn) {
            rejectBtn.disabled = false;
        }
    }
}
window.approvePhase1 = approvePhase1;

async function rejectPhase1() {
    if (!projectId || !currentReviewingAgentType) {
        showStatus('No document available for rejection', 'error');
        return;
    }
    
    // Confirm rejection
    if (!confirm(`Are you sure you want to reject ${currentReviewingDocument || 'this document'}? This will stop the workflow.`)) {
        return;
    }
    
    const approveBtn = document.getElementById('approvePhase1Btn');
    const rejectBtn = document.getElementById('rejectPhase1Btn');
    const notesText = document.getElementById('approvalNotesText');
    
    // Disable buttons
    if (approveBtn) approveBtn.disabled = true;
    if (rejectBtn) rejectBtn.disabled = true;
    if (rejectBtn) rejectBtn.textContent = 'Rejecting...';
    
    try {
        const notes = notesText ? notesText.value.trim() || null : null;
        const response = await fetch(`/api/reject-document/${projectId}/${currentReviewingAgentType}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes: notes })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        showStatus(`${currentReviewingDocument || 'Document'} rejected. Workflow stopped.`, 'error');
        hideDocumentReview();
        
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Documentation';
            generateBtn.classList.remove('loading');
        }
        if (progressDiv) {
            progressDiv.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error rejecting document:', error);
        showStatus('Error rejecting document: ' + error.message, 'error');
        if (approveBtn) approveBtn.disabled = false;
        if (rejectBtn) {
            rejectBtn.disabled = false;
            rejectBtn.textContent = '❌ Reject & Stop';
        }
    }
}
window.rejectPhase1 = rejectPhase1;

// Keyboard shortcuts for approval workflow
document.addEventListener('keydown', (e) => {
    const phase1Review = document.getElementById('phase1Review');
    if (!phase1Review || phase1Review.classList.contains('hidden')) {
        return; // Approval UI not visible
    }
    
    const notesText = document.getElementById('approvalNotesText');
    const isTypingInNotes = notesText && document.activeElement === notesText;
    
    // Enter key: Approve (if not typing in notes, or Ctrl+Enter)
    if (e.key === 'Enter' && (!isTypingInNotes || e.ctrlKey)) {
        e.preventDefault();
        if (!isTypingInNotes || e.ctrlKey) {
            approvePhase1();
        }
    }
    
    // Esc key: Cancel/Close (only if not typing in notes)
    if (e.key === 'Escape' && !isTypingInNotes) {
        e.preventDefault();
        // Don't auto-reject, just close the review UI
        // User can manually reject if needed
    }
});

