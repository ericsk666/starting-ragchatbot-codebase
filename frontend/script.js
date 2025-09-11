// API base URL - use relative path to work from any host
const API_URL = '/api';

// Global state
let currentSessionId = null;

// DOM elements
let chatMessages, chatInput, sendButton, totalCourses, courseTitles;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements after page loads
    chatMessages = document.getElementById('chatMessages');
    chatInput = document.getElementById('chatInput');
    sendButton = document.getElementById('sendButton');
    totalCourses = document.getElementById('totalCourses');
    courseTitles = document.getElementById('courseTitles');
    
    setupEventListeners();
    createNewSession();
    loadCourseStats();
});

// Event Listeners
function setupEventListeners() {
    // Chat functionality
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    // 推荐问题气泡点击
    document.querySelectorAll('.bubble-item').forEach(button => {
        button.addEventListener('click', (e) => {
            const question = e.target.getAttribute('data-question');
            chatInput.value = question;
            sendMessage();
        });
    });
}


// Chat Functions
async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;

    // Disable input
    chatInput.value = '';
    chatInput.disabled = true;
    sendButton.disabled = true;

    // Add user message
    addMessage(query, 'user');

    // Add loading message - create a unique container for it
    const loadingMessage = createLoadingMessage();
    chatMessages.appendChild(loadingMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                session_id: currentSessionId
            })
        });

        if (!response.ok) throw new Error('查询失败');

        const data = await response.json();
        
        // Update session ID if new
        if (!currentSessionId) {
            currentSessionId = data.session_id;
        }

        // Replace loading message with response
        loadingMessage.remove();
        addMessage(data.answer, 'assistant', data.sources, false, data.sources_detail);

    } catch (error) {
        // Replace loading message with error
        loadingMessage.remove();
        addMessage(`错误：${error.message}`, 'assistant');
    } finally {
        chatInput.disabled = false;
        sendButton.disabled = false;
        chatInput.focus();
    }
}

function createLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="loading">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span class="loading-text">思考中...</span>
        </div>
    `;
    return messageDiv;
}

function addMessage(content, type, sources = null, isWelcome = false, sourcesDetail = null) {
    const messageId = Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}${isWelcome ? ' welcome-message' : ''}`;
    messageDiv.id = `message-${messageId}`;
    
    // Convert markdown to HTML for assistant messages
    const displayContent = type === 'assistant' ? marked.parse(content) : escapeHtml(content);
    
    let html = `<div class="message-content">${displayContent}</div>`;
    
    if (sources && sources.length > 0) {
        html += `
            <details class="sources-collapsible">
                <summary class="sources-header">参考来源</summary>
                <div class="sources-content">`;
        
        // If we have detailed sources with links, use them
        if (sourcesDetail && sourcesDetail.length > 0) {
            const sourcesHtml = sourcesDetail.map((source, index) => {
                // Determine which link to use (prefer lesson_link over course_link)
                const link = source.lesson_link || source.course_link;
                
                if (link) {
                    // Create clickable link
                    return `<a href="${link}" target="_blank" class="source-link" rel="noopener noreferrer">
                        ${escapeHtml(source.title)}
                        <span class="external-icon">↗</span>
                    </a>`;
                } else {
                    // No link available, show as plain text
                    return `<span class="source-plain">${escapeHtml(source.title)}</span>`;
                }
            }).join('<span class="source-separator">, </span>');
            
            html += sourcesHtml;
        } else {
            // Fallback to simple text sources
            html += sources.join(', ');
        }
        
        html += `</div>
            </details>
        `;
    }
    
    messageDiv.innerHTML = html;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageId;
}

// Helper function to escape HTML for user messages
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Removed removeMessage function - no longer needed since we handle loading differently

async function createNewSession() {
    currentSessionId = null;
    chatMessages.innerHTML = '';
    addMessage('欢迎使用AI学习助手！我可以帮您解答关于课程、教学内容和具体知识点的问题。您想了解什么？', 'assistant', null, true);
}

// Load course statistics
async function loadCourseStats() {
    try {
        console.log('加载课程统计...');
        const response = await fetch(`${API_URL}/courses`);
        if (!response.ok) throw new Error('加载课程统计失败');
        
        const data = await response.json();
        console.log('收到课程数据：', data);
        
        // Update stats in UI
        const totalCoursesElem = document.getElementById('totalCourses');
        if (totalCoursesElem) {
            totalCoursesElem.textContent = data.total_courses || '0';
        }
        
        // Update resources list with file-like display
        const resourcesList = document.getElementById('resourcesList');
        if (resourcesList) {
            if (data.course_titles && data.course_titles.length > 0) {
                resourcesList.innerHTML = data.course_titles
                    .map(title => `
                        <div class="resource-item">
                            <span class="resource-icon">📄</span>
                            <span class="resource-name">${title}</span>
                        </div>
                    `)
                    .join('');
            } else {
                resourcesList.innerHTML = '<div class="no-resources">暂无课程资源</div>';
            }
        }
        
    } catch (error) {
        console.error('加载课程统计错误：', error);
        // Set default values on error
        const totalCoursesElem = document.getElementById('totalCourses');
        if (totalCoursesElem) {
            totalCoursesElem.textContent = '0';
        }
        const resourcesList = document.getElementById('resourcesList');
        if (resourcesList) {
            resourcesList.innerHTML = '<div class="error-message">加载失败</div>';
        }
    }
}