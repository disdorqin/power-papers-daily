/**
 * SOTA Papers Daily - 前端展示逻辑
 * 按时间顺序展示 SOTA 论文，每页 20 篇
 */

// ============================================================
// 配置
// ============================================================

const SOTA_CONFIG = {
    dataUrl: 'data/sota_papers_AI_enhanced_Chinese.jsonl',
    fallbackUrl: 'data/sota_papers.jsonl',
    papersPerPage: 20,
};

// ============================================================
// 全局状态
// ============================================================

let allPapers = [];
let filteredPapers = [];
let currentPage = 1;
let currentFilter = 'all';

// ============================================================
// 数据加载
// ============================================================

async function loadPapers() {
    const container = document.getElementById('paperContainer');
    container.innerHTML = `
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <p>Loading SOTA papers...</p>
        </div>
    `;

    try {
        // 尝试加载增强版数据
        let response = await fetch(SOTA_CONFIG.dataUrl);
        if (!response.ok) {
            // 回退到原始数据
            response = await fetch(SOTA_CONFIG.fallbackUrl);
            if (!response.ok) {
                throw new Error('Failed to load papers data');
            }
        }

        const text = await response.text();
        allPapers = parseJsonlData(text);
        
        // 按时间倒序排序（最新的在前）
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
                <p style="font-size: 0.9rem; color: #6b7280; margin-top: 0.5rem;">
                    Error: ${error.message}
                </p>
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

// ============================================================
// 渲染逻辑
// ============================================================

function renderPapers() {
    const container = document.getElementById('paperContainer');
    
    if (filteredPapers.length === 0) {
        container.innerHTML = `
            <div class="loading-container">
                <p>No SOTA papers found.</p>
            </div>
        `;
        return;
    }

    // 计算当前页的论文范围
    const startIndex = (currentPage - 1) * SOTA_CONFIG.papersPerPage;
    const endIndex = Math.min(startIndex + SOTA_CONFIG.papersPerPage, filteredPapers.length);
    const papersToShow = filteredPapers.slice(startIndex, endIndex);

    container.innerHTML = '';
    
    papersToShow.forEach((paper, index) => {
        const card = createPaperCard(paper, startIndex + index + 1);
        container.appendChild(card);
    });
}

function createPaperCard(paper, index) {
    const card = document.createElement('div');
    card.className = 'paper-card';
    
    // 检查是否有 GitHub 代码
    const hasCode = paper.github_url || (paper.code_info && paper.code_info.code_url);
    if (hasCode) {
        card.classList.add('has-code');
    }

    // 标题
    const title = document.createElement('h3');
    title.className = 'paper-title';
    const titleLink = document.createElement('a');
    titleLink.href = paper.arxiv_url || paper.pdf_url || '#';
    titleLink.target = '_blank';
    titleLink.textContent = paper.title || 'Untitled';
    title.appendChild(titleLink);
    card.appendChild(title);

    // 作者
    if (paper.authors && paper.authors.length > 0) {
        const authors = document.createElement('p');
        authors.className = 'paper-authors';
        authors.textContent = paper.authors.slice(0, 3).join(', ') + 
            (paper.authors.length > 3 ? ' et al.' : '');
        card.appendChild(authors);
    }

    // 元信息
    const meta = document.createElement('div');
    meta.className = 'paper-meta';
    
    // 会议标签
    if (paper.conference) {
        const confTag = document.createElement('span');
        confTag.className = 'paper-conference';
        confTag.textContent = paper.conference;
        meta.appendChild(confTag);
    }
    
    // 日期
    if (paper.published || paper.collected_at) {
        const dateTag = document.createElement('span');
        dateTag.className = 'paper-date';
        const dateStr = paper.published || paper.collected_at;
        dateTag.textContent = new Date(dateStr).toLocaleDateString('zh-CN');
        meta.appendChild(dateTag);
    }
    
    card.appendChild(meta);

    // 标签
    const tags = document.createElement('div');
    tags.className = 'paper-tags';
    
    // SOTA 标签
    const sotaTag = document.createElement('span');
    sotaTag.className = 'paper-tag sota';
    sotaTag.textContent = '🔥 SOTA';
    tags.appendChild(sotaTag);
    
    // 代码标签
    if (hasCode) {
        const codeTag = document.createElement('span');
        codeTag.className = 'paper-tag code';
        codeTag.textContent = '💻 Code';
        tags.appendChild(codeTag);
    }
    
    // 领域标签
    const domainTags = detectDomainTags(paper);
    domainTags.forEach(tagText => {
        const tag = document.createElement('span');
        tag.className = 'paper-tag';
        tag.textContent = tagText;
        tags.appendChild(tag);
    });
    
    card.appendChild(tags);

    // 摘要
    if (paper.details || paper.summary) {
        const summary = document.createElement('p');
        summary.className = 'paper-summary';
        summary.textContent = (paper.details || paper.summary).substring(0, 300) + '...';
        card.appendChild(summary);
    }

    // 链接
    const links = document.createElement('div');
    links.className = 'paper-links';
    
    // arXiv 链接
    if (paper.arxiv_url) {
        const arxivLink = document.createElement('a');
        arxivLink.className = 'paper-link';
        arxivLink.href = paper.arxiv_url;
        arxivLink.target = '_blank';
        arxivLink.innerHTML = '📄 arXiv';
        links.appendChild(arxivLink);
    }
    
    // PDF 链接
    if (paper.pdf_url) {
        const pdfLink = document.createElement('a');
        pdfLink.className = 'paper-link pdf';
        pdfLink.href = paper.pdf_url;
        pdfLink.target = '_blank';
        pdfLink.innerHTML = '📥 PDF';
        links.appendChild(pdfLink);
    }
    
    // GitHub 链接
    const githubUrl = paper.github_url || (paper.code_info && paper.code_info.code_url);
    if (githubUrl) {
        const githubLink = document.createElement('a');
        githubLink.className = 'paper-link github';
        githubLink.href = githubUrl;
        githubLink.target = '_blank';
        githubLink.innerHTML = '⭐ GitHub';
        if (paper.code_info && paper.code_info.stars) {
            githubLink.innerHTML += ` (${paper.code_info.stars} ⭐)`;
        }
        links.appendChild(githubLink);
    }
    
    card.appendChild(links);

    return card;
}

function detectDomainTags(paper) {
    const tags = [];
    const text = `${paper.title} ${paper.summary} ${paper.details}`.toLowerCase();
    
    if (text.includes('time series') || text.includes('time-series') || text.includes('forecasting')) {
        tags.push('时序预测');
    }
    if (text.includes('power') || text.includes('electricity') || text.includes('energy') || text.includes('load')) {
        tags.push('电力预测');
    }
    if (text.includes('vision') || text.includes('image') || text.includes('cv')) {
        tags.push('计算机视觉');
    }
    if (text.includes('language') || text.includes('llm') || text.includes('nlp')) {
        tags.push('自然语言');
    }
    if (text.includes('graph') || text.includes('gnn')) {
        tags.push('图神经网络');
    }
    
    return tags;
}

// ============================================================
// 分页逻辑
// ============================================================

function renderPagination() {
    const totalPages = Math.ceil(filteredPapers.length / SOTA_CONFIG.papersPerPage);
    
    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = currentPage === totalPages || totalPages === 0;
    document.getElementById('pageInfo').textContent = `第 ${currentPage} / ${totalPages} 页 (共 ${filteredPapers.length} 篇)`;
}

function goToPage(page) {
    const totalPages = Math.ceil(filteredPapers.length / SOTA_CONFIG.papersPerPage);
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    renderPapers();
    renderPagination();
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================================
// 过滤逻辑
// ============================================================

function applyFilter(filter) {
    currentFilter = filter;
    
    if (filter === 'all') {
        filteredPapers = [...allPapers];
    } else {
        filteredPapers = allPapers.filter(paper => {
            const text = `${paper.title} ${paper.summary} ${paper.details}`.toLowerCase();
            
            switch (filter) {
                case 'cv':
                    return text.includes('vision') || text.includes('image') || 
                           text.includes('cv') || paper.conference?.includes('CVPR') ||
                           paper.conference?.includes('ICCV') || paper.conference?.includes('ECCV');
                case 'ml':
                    return text.includes('learning') || text.includes('model') ||
                           paper.conference?.includes('NeurIPS') || paper.conference?.includes('ICML') ||
                           paper.conference?.includes('ICLR');
                case 'time-series':
                    return text.includes('time series') || text.includes('time-series') ||
                           text.includes('forecasting') || text.includes('temporal');
                case 'power':
                    return text.includes('power') || text.includes('electricity') ||
                           text.includes('energy') || text.includes('load') ||
                           text.includes('grid');
                default:
                    return true;
            }
        });
    }
    
    currentPage = 1;
    renderPapers();
    renderPagination();
}

// ============================================================
// 事件绑定
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    // 加载论文
    loadPapers();
    
    // 分页按钮
    document.getElementById('prevPage').addEventListener('click', () => goToPage(currentPage - 1));
    document.getElementById('nextPage').addEventListener('click', () => goToPage(currentPage + 1));
    
    // 过滤标签
    document.querySelectorAll('.filter-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            document.querySelectorAll('.filter-tag').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            applyFilter(this.dataset.filter);
        });
    });
});
