/**
 * SOTA Papers Daily - 前端展示逻辑
 * 按时间顺序展示 SOTA 论文，每页 20 篇
 */

const SOTA_CONFIG = {
    dataUrl: 'data/sota_papers.jsonl',
    papersPerPage: 20,
};

let allPapers = [];
let filteredPapers = [];
let currentPage = 1;
let currentFilter = 'all';

async function loadPapers() {
    const container = document.getElementById('paperContainer');
    container.innerHTML = `
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <p>Loading SOTA papers...</p>
        </div>
    `;

    try {
        const response = await fetch(SOTA_CONFIG.dataUrl);
        if (!response.ok) {
            throw new Error('Failed to load papers data');
        }

        const text = await response.text();
        allPapers = parseJsonlData(text);
        
        allPapers.sort((a, b) => {
            const dateA = new Date(a.published || a.collected_at || 0);
            const dateB = new Date(b.published || b.collected_at || 0);
            return dateB - dateA;
        });

        filteredPapers = [...allPapers];
        currentPage = 1;
        
        renderPapers();
        renderPagination();
        
    } catch (error) {
        console.error('Error loading papers:', error);
        container.innerHTML = `
            <div class="loading-container">
                <p>Failed to load papers. Please try again later.</p>
            </div>
        `;
    }
}

function parseJsonlData(text) {
    const papers = [];
    const lines = text.trim().split('\n');
    
    for (const line of lines) {
        if (line.trim()) {
            try {
                papers.push(JSON.parse(line));
            } catch (e) {
                console.warn('Failed to parse line:', e);
            }
        }
    }
    
    return papers;
}

function renderPapers() {
    const container = document.getElementById('paperContainer');
    
    if (filteredPapers.length === 0) {
        container.innerHTML = `
            <div class="loading-container">
                <p>No papers found matching the current filter.</p>
            </div>
        `;
        return;
    }
    
    const start = (currentPage - 1) * SOTA_CONFIG.papersPerPage;
    const end = start + SOTA_CONFIG.papersPerPage;
    const pagePapers = filteredPapers.slice(start, end);
    
    container.innerHTML = pagePapers.map(paper => createPaperCard(paper)).join('');
}

function createPaperCard(paper) {
    const hasCode = paper.github_url && paper.github_url.trim() !== '';
    const date = paper.published || paper.collected_at || '';
    const dateStr = date ? new Date(date).toLocaleDateString('zh-CN') : '';
    
    let tags = [];
    if (paper.categories) {
        tags = paper.categories.slice(0, 3);
    }
    
    return `
        <div class="paper-card ${hasCode ? 'has-code' : ''}">
            <h3 class="paper-title">
                <a href="${paper.arxiv_url || paper.pdf_url || '#' }" target="_blank">${paper.title}</a>
            </h3>
            <p class="paper-authors">${(paper.authors || []).slice(0, 5).join(', ')}</p>
            <div class="paper-meta">
                <span class="paper-conference">${paper.conference || 'arXiv'}</span>
                <span class="paper-date">${dateStr}</span>
            </div>
            <div class="paper-tags">
                <span class="paper-tag sota">🔥 SOTA</span>
                ${hasCode ? '<span class="paper-tag code">💻 Code</span>' : ''}
                ${tags.map(tag => `<span class="paper-tag">${tag}</span>`).join('')}
            </div>
            ${paper.summary ? `<p class="paper-summary">${paper.summary.slice(0, 300)}...</p>` : ''}
            <div class="paper-links">
                ${paper.arxiv_url ? `<a href="${paper.arxiv_url}" target="_blank" class="paper-link">📄 arXiv</a>` : ''}
                ${paper.pdf_url ? `<a href="${paper.pdf_url}" target="_blank" class="paper-link pdf">📑 PDF</a>` : ''}
                ${hasCode ? `<a href="${paper.github_url}" target="_blank" class="paper-link github">⭐ GitHub</a>` : ''}
            </div>
        </div>
    `;
}

function renderPagination() {
    const totalPages = Math.ceil(filteredPapers.length / SOTA_CONFIG.papersPerPage);
    
    document.getElementById('pageInfo').textContent = `第 ${currentPage} / ${totalPages} 页 (共 ${filteredPapers.length} 篇)`;
    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = currentPage === totalPages || totalPages === 0;
}

function filterPapers(filter) {
    currentFilter = filter;
    
    if (filter === 'all') {
        filteredPapers = [...allPapers];
    } else if (filter === 'cv') {
        filteredPapers = allPapers.filter(p => 
            p.categories && p.categories.some(c => 
                c.includes('CV') || c.includes('cs.CV') || c.includes('eess.IV')
            )
        );
    } else if (filter === 'ml') {
        filteredPapers = allPapers.filter(p => 
            p.categories && p.categories.some(c => 
                c.includes('LG') || c.includes('cs.LG') || c.includes('stat.ML')
            )
        );
    } else if (filter === 'time-series') {
        filteredPapers = allPapers.filter(p => 
            p.title.toLowerCase().includes('time series') ||
            p.title.toLowerCase().includes('forecasting') ||
            p.summary && p.summary.toLowerCase().includes('time series')
        );
    } else if (filter === 'power') {
        filteredPapers = allPapers.filter(p => 
            p.title.toLowerCase().includes('power') ||
            p.title.toLowerCase().includes('energy') ||
            p.title.toLowerCase().includes('electricity') ||
            p.summary && p.summary.toLowerCase().includes('power load')
        );
    }
    
    currentPage = 1;
    renderPapers();
    renderPagination();
}

document.addEventListener('DOMContentLoaded', () => {
    loadPapers();
    
    document.querySelectorAll('.filter-tag').forEach(tag => {
        tag.addEventListener('click', () => {
            document.querySelectorAll('.filter-tag').forEach(t => t.classList.remove('active'));
            tag.classList.add('active');
            filterPapers(tag.dataset.filter);
        });
    });
    
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderPapers();
            renderPagination();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });
    
    document.getElementById('nextPage').addEventListener('click', () => {
        const totalPages = Math.ceil(filteredPapers.length / SOTA_CONFIG.papersPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            renderPapers();
            renderPagination();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });
});