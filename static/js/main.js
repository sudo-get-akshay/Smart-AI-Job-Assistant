// ============================================
// GLOBAL STATE
// ============================================
let sessionId = null;
let currentJobs = [];
let currentResearch = {};

// ============================================
// PARTICLE ANIMATION
// ============================================
function initParticles() {
    const canvas = document.getElementById('particleCanvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    const particleCount = 80;
    
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 1;
            this.speedX = Math.random() * 0.5 - 0.25;
            this.speedY = Math.random() * 0.5 - 0.25;
            this.opacity = Math.random() * 0.5 + 0.2;
        }
        
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            
            if (this.x > canvas.width) this.x = 0;
            if (this.x < 0) this.x = canvas.width;
            if (this.y > canvas.height) this.y = 0;
            if (this.y < 0) this.y = canvas.height;
        }
        
        draw() {
            ctx.fillStyle = `rgba(99, 102, 241, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        // Draw connections
        particles.forEach((p1, i) => {
            particles.slice(i + 1).forEach(p2 => {
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 150) {
                    ctx.strokeStyle = `rgba(99, 102, 241, ${0.1 * (1 - distance / 150)})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            });
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
    
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// ============================================
// NAVIGATION
// ============================================
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page-section');
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetPage = link.dataset.page;
            
            // Update active states
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Switch pages
            pages.forEach(page => {
                if (page.id === targetPage) {
                    page.classList.add('active');
                } else {
                    page.classList.remove('active');
                }
            });
            
            // Close mobile menu
            navMenu.classList.remove('active');
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });
    
    // Hamburger menu
    hamburger.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });
}

// Navigate to specific page (helper function)
function navigateToPage(pageName) {
    const link = document.querySelector(`[data-page="${pageName}"]`);
    if (link) link.click();
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ============================================
// LOADING OVERLAY
// ============================================
function showLoading(text = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    loadingText.textContent = text;
    overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.remove('active');
}

// ============================================
// RESUME UPLOAD
// ============================================
function initResumeUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const resumeInput = document.getElementById('resumeInput');
    const resumePreview = document.getElementById('resumePreview');
    const removeFileBtn = document.getElementById('removeFile');
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#6366f1';
        uploadArea.style.background = 'rgba(99, 102, 241, 0.1)';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'rgba(99, 102, 241, 0.3)';
        uploadArea.style.background = 'transparent';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'rgba(99, 102, 241, 0.3)';
        uploadArea.style.background = 'transparent';
        
        const file = e.dataTransfer.files[0];
        if (file && file.type === 'application/pdf') {
            uploadResume(file);
        } else {
            showToast('Please upload a PDF file', 'error');
        }
    });
    
    // File input change
    resumeInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            uploadResume(file);
        }
    });
    
    // Remove file
    removeFileBtn.addEventListener('click', () => {
        sessionId = null;
        resumePreview.style.display = 'none';
        uploadArea.style.display = 'block';
        resumeInput.value = '';
        updateStats({ skills: 0 });
        showToast('Resume removed', 'info');
    });
}

async function uploadResume(file) {
    showLoading('Analyzing your resume...');
    
    const formData = new FormData();
    formData.append('resume', file);
    
    try {
        const response = await fetch('/upload-resume', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            sessionId = data.session_id;
            displayResumePreview(data.filename, data.skills);
            updateStats({ skills: data.skills.length });
            showToast('Resume analyzed successfully!', 'success');
        } else {
            showToast(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
}

function displayResumePreview(filename, skills) {
    const uploadArea = document.getElementById('uploadArea');
    const resumePreview = document.getElementById('resumePreview');
    const fileNameSpan = document.getElementById('fileName');
    const skillTags = document.getElementById('skillTags');
    
    uploadArea.style.display = 'none';
    resumePreview.style.display = 'block';
    fileNameSpan.textContent = filename;
    
    skillTags.innerHTML = skills.map(skill => 
        `<span class="skill-tag">${skill}</span>`
    ).join('');
}

// ============================================
// JOB SEARCH
// ============================================
function initJobSearch() {
    const searchBtn = document.getElementById('searchJobsBtn');
    
    searchBtn.addEventListener('click', async () => {
        if (!sessionId) {
            showToast('Please upload your resume first', 'error');
            return;
        }
        
        const location = document.getElementById('location').value;
        const limit = parseInt(document.getElementById('jobLimit').value);
        
        showLoading('Finding perfect jobs for you...');
        
        try {
            const response = await fetch('/search-jobs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    location,
                    limit
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                currentJobs = data.jobs;
                displayJobs(data.jobs);
                updateStats({ jobs: data.jobs.length });
                showToast(`Found ${data.jobs.length} jobs!`, 'success');
                
                // Navigate to jobs page
                setTimeout(() => navigateToPage('jobs'), 500);
            } else {
                showToast(data.error || 'Search failed', 'error');
            }
        } catch (error) {
            showToast('Network error. Please try again.', 'error');
            console.error(error);
        } finally {
            hideLoading();
        }
    });
}

// FIXED: displayJobs function using proper event listeners
function displayJobs(jobs) {
    const container = document.getElementById('jobsContainer');
    
    if (jobs.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-briefcase"></i>
                <h3>No Jobs Found</h3>
                <p>Try adjusting your search criteria</p>
                <button class="btn btn-primary" onclick="navigateToPage('home')">
                    <i class="fas fa-search"></i>
                    Search Again
                </button>
            </div>
        `;
        return;
    }
    
    // Clear container
    container.innerHTML = '';
    
    // Create job cards with proper event listeners
    jobs.forEach((job, index) => {
        const jobCard = document.createElement('div');
        jobCard.className = 'job-card';
        
        jobCard.innerHTML = `
            <div class="job-header">
                <div class="job-info">
                    <h3>${escapeHtml(job.title)}</h3>
                    <div class="job-company">
                        <i class="fas fa-building"></i>
                        <span>${escapeHtml(job.company)}</span>
                    </div>
                    <div class="job-location">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${escapeHtml(job.location)}</span>
                    </div>
                </div>
                <div class="job-actions" data-job-index="${index}">
                </div>
            </div>
            <div class="job-description">
                ${escapeHtml(job.description)}
            </div>
        `;
        
        // Add action buttons with event listeners
        const actionsDiv = jobCard.querySelector('.job-actions');
        
        // View Job button
        const viewBtn = document.createElement('a');
        viewBtn.href = job.link;
        viewBtn.target = '_blank';
        viewBtn.className = 'btn btn-primary';
        viewBtn.innerHTML = '<i class="fas fa-external-link-alt"></i> View Job';
        actionsDiv.appendChild(viewBtn);
        
        // Cover Letter button
        const coverBtn = document.createElement('button');
        coverBtn.className = 'btn btn-secondary';
        coverBtn.innerHTML = '<i class="fas fa-file-alt"></i> Cover Letter';
        coverBtn.addEventListener('click', () => generateCoverLetter(index));
        actionsDiv.appendChild(coverBtn);
        
        // Research button
        const researchBtn = document.createElement('button');
        researchBtn.className = 'btn btn-secondary';
        researchBtn.innerHTML = '<i class="fas fa-search"></i> Research';
        researchBtn.addEventListener('click', () => researchCompanyFromJob(index));
        actionsDiv.appendChild(researchBtn);
        
        container.appendChild(jobCard);
    });
}

// Helper function to escape HTML
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

// Helper function to research company from job index
function researchCompanyFromJob(jobIndex) {
    const job = currentJobs[jobIndex];
    researchCompany(job.company, job.title);
}

// ============================================
// COVER LETTER
// ============================================
async function generateCoverLetter(jobIndex) {
    if (!sessionId) {
        showToast('Session expired. Please upload resume again.', 'error');
        navigateToPage('home');
        return;
    }
    
    if (jobIndex < 0 || jobIndex >= currentJobs.length) {
        showToast('Invalid job selection', 'error');
        return;
    }
    
    const job = currentJobs[jobIndex];
    showLoading('Generating personalized cover letter...');
    
    try {
        const response = await fetch('/generate-cover-letter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                job: job
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showCoverLetterModal(data.cover_letter, job.company);
            showToast('Cover letter generated!', 'success');
        } else {
            showToast(data.error || 'Generation failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
        console.error('Cover letter generation error:', error);
    } finally {
        hideLoading();
    }
}

function showCoverLetterModal(letter, companyName) {
    const modal = document.getElementById('coverLetterModal');
    const textarea = document.getElementById('coverLetterText');
    const closeBtn = modal.querySelector('.modal-close');
    const copyBtn = document.getElementById('copyCoverLetter');
    const downloadBtn = document.getElementById('downloadCoverLetter');
    
    textarea.value = letter;
    modal.classList.add('active');
    
    // Remove old event listeners by cloning
    const newCloseBtn = closeBtn.cloneNode(true);
    closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);
    const newCopyBtn = copyBtn.cloneNode(true);
    copyBtn.parentNode.replaceChild(newCopyBtn, copyBtn);
    const newDownloadBtn = downloadBtn.cloneNode(true);
    downloadBtn.parentNode.replaceChild(newDownloadBtn, downloadBtn);
    
    // Add new event listeners
    newCloseBtn.addEventListener('click', () => modal.classList.remove('active'));
    
    newCopyBtn.addEventListener('click', () => {
        textarea.select();
        document.execCommand('copy');
        showToast('Copied to clipboard!', 'success');
    });
    
    newDownloadBtn.addEventListener('click', () => {
        const blob = new Blob([letter], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cover_letter_${companyName.replace(/[^a-z0-9]/gi, '_')}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('Downloaded!', 'success');
    });
    
    // Close on outside click
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    };
}

// ============================================
// SKILL GAP ANALYSIS
// ============================================
function initSkillAnalysis() {
    const analyzeBtn = document.getElementById('analyzeSkillsBtn');
    
    analyzeBtn.addEventListener('click', async () => {
        if (!sessionId) {
            showToast('Please upload your resume first', 'error');
            navigateToPage('home');
            return;
        }
        
        const jobDescription = document.getElementById('jobDescription').value;
        
        if (!jobDescription.trim()) {
            showToast('Please paste a job description', 'error');
            return;
        }
        
        showLoading('Analyzing skill gaps...');
        
        try {
            const response = await fetch('/analyze-skills', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    job_description: jobDescription
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                displaySkillAnalysis(data.analysis);
                
                if (data.analysis.missing_skills.length > 0) {
                    await fetchCourses(data.analysis.missing_skills);
                }
                
                showToast('Analysis complete!', 'success');
            } else {
                showToast(data.error || 'Analysis failed', 'error');
            }
        } catch (error) {
            showToast('Network error. Please try again.', 'error');
            console.error(error);
        } finally {
            hideLoading();
        }
    });
}

function displaySkillAnalysis(analysis) {
    const resultDiv = document.getElementById('skillAnalysisResult');
    const matchedList = document.getElementById('matchedSkillsList');
    const missingList = document.getElementById('missingSkillsList');
    
    resultDiv.style.display = 'block';
    
    matchedList.innerHTML = analysis.matched_skills.map(skill => `
        <div class="skill-item">
            <i class="fas fa-check-circle"></i>
            <span>${escapeHtml(skill)}</span>
        </div>
    `).join('');
    
    missingList.innerHTML = analysis.missing_skills.length > 0
        ? analysis.missing_skills.map(skill => `
            <div class="skill-item">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${escapeHtml(skill)}</span>
            </div>
        `).join('')
        : '<p style="text-align: center; color: #22c55e;">Great! No skill gaps found.</p>';
}

async function fetchCourses(skills) {
    showLoading('Finding learning resources...');
    
    try {
        const response = await fetch('/get-courses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ skills })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayCourses(data.courses);
            updateStats({ courses: data.courses.length });
        }
    } catch (error) {
        console.error('Failed to fetch courses:', error);
    } finally {
        hideLoading();
    }
}

function displayCourses(courses) {
    const container = document.getElementById('coursesContainer');
    
    container.innerHTML = courses.map(courseSet => `
        <div class="course-section">
            <h3>
                <i class="fas fa-graduation-cap"></i>
                Learn ${escapeHtml(courseSet.skill)}
            </h3>
            <div class="course-grid">
                ${courseSet.youtube.map(course => `
                    <div class="course-item">
                        <div class="course-info">
                            <i class="fab fa-youtube"></i>
                            <div>
                                <div>${escapeHtml(course.title)}</div>
                                <span class="course-platform">${escapeHtml(course.platform)}</span>
                            </div>
                        </div>
                        <a href="${escapeHtml(course.url)}" target="_blank" class="btn btn-secondary">
                            <i class="fas fa-external-link-alt"></i>
                            Watch
                        </a>
                    </div>
                `).join('')}
                ${courseSet.curated.map(course => `
                    <div class="course-item">
                        <div class="course-info">
                            <i class="fas fa-book"></i>
                            <div>
                                <div>${escapeHtml(course.title)}</div>
                                <span class="course-platform">${escapeHtml(course.platform)}</span>
                            </div>
                        </div>
                        <a href="${escapeHtml(course.url)}" target="_blank" class="btn btn-secondary">
                            <i class="fas fa-external-link-alt"></i>
                            Enroll
                        </a>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

// ============================================
// COMPANY RESEARCH
// ============================================
function initCompanyResearch() {
    const researchBtn = document.getElementById('researchBtn');
    
    researchBtn.addEventListener('click', async () => {
        const companyName = document.getElementById('companyName').value;
        const jobTitle = document.getElementById('jobTitle').value;
        
        if (!companyName.trim() || !jobTitle.trim()) {
            showToast('Please enter both company name and job title', 'error');
            return;
        }
        
        await researchCompany(companyName, jobTitle);
    });
}

async function researchCompany(companyName, jobTitle) {
    showLoading(`Researching ${companyName}...`);
    
    try {
        const response = await fetch('/research-company', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                company_name: companyName,
                job_title: jobTitle
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentResearch = data.research;
            displayResearch(data.research);
            updateStats({ companiesResearched: 1 });
            showToast('Research complete!', 'success');
            
            // Navigate to research page if not already there
            if (!document.getElementById('research').classList.contains('active')) {
                navigateToPage('research');
            }
        } else {
            showToast(data.error || 'Research failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
}

function displayResearch(research) {
    const resultsDiv = document.getElementById('researchResults');
    const briefContent = document.getElementById('briefContent');
    const newsTab = document.getElementById('news');
    const cultureTab = document.getElementById('culture');
    const questionsTab = document.getElementById('questions');
    
    resultsDiv.style.display = 'block';
    
    // AI Brief
    briefContent.innerHTML = marked.parse(research.ai_brief);
    
    // News
    newsTab.innerHTML = research.company_info.news.length > 0
        ? research.company_info.news.map(item => `
            <div class="info-item">
                <h4><a href="${escapeHtml(item.link)}" target="_blank">${escapeHtml(item.title)}</a></h4>
                <p>${escapeHtml(item.snippet)}</p>
            </div>
        `).join('')
        : '<p style="text-align: center; color: #64748b;">No recent news found.</p>';
    
    // Culture
    const cultureItems = [
        ...research.company_info.culture,
        ...research.company_info.hiring
    ];
    
    cultureTab.innerHTML = cultureItems.length > 0
        ? cultureItems.map(item => `
            <div class="info-item">
                <h4><a href="${escapeHtml(item.link)}" target="_blank">${escapeHtml(item.title)}</a></h4>
                <p>${escapeHtml(item.snippet)}</p>
            </div>
        `).join('')
        : '<p style="text-align: center; color: #64748b;">No culture information found.</p>';
    
    // Interview Q&A
    questionsTab.innerHTML = research.interview_questions.length > 0
        ? research.interview_questions.map(item => `
            <div class="info-item">
                <h4><a href="${escapeHtml(item.link)}" target="_blank">${escapeHtml(item.source)}</a></h4>
                <p>${escapeHtml(item.snippet)}</p>
            </div>
        `).join('')
        : '<p style="text-align: center; color: #64748b;">No interview questions found.</p>';
    
    // Download button
    const downloadBtn = document.getElementById('downloadBrief');
    const newDownloadBtn = downloadBtn.cloneNode(true);
    downloadBtn.parentNode.replaceChild(newDownloadBtn, downloadBtn);
    
    newDownloadBtn.addEventListener('click', () => {
        const blob = new Blob([research.ai_brief], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `interview_brief_${research.company_name.replace(/[^a-z0-9]/gi, '_')}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('Downloaded!', 'success');
    });
}

function initResearchTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.dataset.tab;
            
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            tabPanels.forEach(panel => {
                if (panel.id === targetTab) {
                    panel.classList.add('active');
                } else {
                    panel.classList.remove('active');
                }
            });
        });
    });
}

// ============================================
// STATS UPDATE
// ============================================
function updateStats(data) {
    if (data.jobs !== undefined) {
        document.getElementById('totalJobs').textContent = data.jobs;
    }
    if (data.skills !== undefined) {
        document.getElementById('totalSkills').textContent = data.skills;
    }
    if (data.companiesResearched !== undefined) {
        const current = parseInt(document.getElementById('companiesResearched').textContent);
        document.getElementById('companiesResearched').textContent = current + data.companiesResearched;
    }
    if (data.courses !== undefined) {
        document.getElementById('coursesFound').textContent = data.courses;
    }
}

// ============================================
// MARKDOWN PARSER (Simple)
// ============================================
const marked = {
    parse(markdown) {
        return markdown
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/<\/p>/g, '</p><p>')
            .replace(/^\n/g, '<br>')
            .replace(/^(.+)$/gm, '<p>$1</p>');
    }
};

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initNavigation();
    initResumeUpload();
    initJobSearch();
    initSkillAnalysis();
    initCompanyResearch();
    initResearchTabs();
    
    console.log('%c🤖 AI Job Assistant Loaded Successfully!', 'color: #6366f1; font-size: 20px; font-weight: bold;');
});

// ============================================
// KEYBOARD SHORTCUTS
// ============================================
document.addEventListener('keydown', (e) => {
    // ESC to close modal
    if (e.key === 'Escape') {
        const modal = document.getElementById('coverLetterModal');
        if (modal.classList.contains('active')) {
            modal.classList.remove('active');
        }
    }
    
    // Ctrl/Cmd + K for quick navigation
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('location');
        searchInput.focus();
    }
});

// ============================================
// SMOOTH SCROLL
// ============================================
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

// ============================================
// PREVENT FORM SUBMISSION ON ENTER
// ============================================
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && input.type !== 'submit') {
            e.preventDefault();
        }
    });
});