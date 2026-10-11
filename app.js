// ByteBreeze Frontend Application Controller
(function() {
  'use strict';

  // Global state
  const state = {
    chapter: 'ai', // 'ai' | 'cyber'
    indexData: null,
    currentEditionData: null,
    searchQuery: '',
    theme: localStorage.getItem('bb-theme') || 'dark'
  };

  // DOM Elements
  const el = {
    brand: document.querySelector('.brand'),
    tabAi: document.getElementById('tab-ai'),
    tabCyber: document.getElementById('tab-cyber'),
    editionSelect: document.getElementById('edition-select'),
    btnCopyMd: document.getElementById('btn-copy-md'),
    btnCopyJson: document.getElementById('btn-copy-json'),
    btnTheme: document.getElementById('btn-theme'),
    searchInput: document.getElementById('search-input'),
    heroTitle: document.getElementById('hero-title'),
    heroDesc: document.getElementById('hero-desc'),
    badgeDate: document.getElementById('badge-date'),
    badgeAudience: document.getElementById('badge-audience'),
    prioritySprint: document.getElementById('priority-sprint'),
    briefingList: document.getElementById('briefing-list'),
    briefingBox: document.getElementById('briefing-box'),
    pillarNav: document.getElementById('pillar-nav'),
    contentArea: document.getElementById('content-area'),
    toast: document.getElementById('toast'),
    lastSyncedTime: document.getElementById('last-synced-time')
  };

  // Initialize
  async function init() {
    applyTheme(state.theme);
    readUrlParams();
    setupEventListeners();

    // Load initial embedded data if available, then fetch latest
    try {
      const embedded = document.getElementById('initial-index-data');
      if (embedded && embedded.textContent.trim()) {
        state.indexData = JSON.parse(embedded.textContent);
      }
    } catch (e) {
      console.warn('No embedded index found, fetching...');
    }

    try {
      const resp = await fetch('data/index.json');
      if (resp.ok) {
        state.indexData = await resp.json();
      }
    } catch (e) {
      console.log('Using local fallback or embedded state', e);
    }

    if (!state.indexData) {
      console.error('Failed to load ByteBreeze index.');
      return;
    }

    updateEditionDropdown();
    await loadEdition();
  }

  function readUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const ch = params.get('chapter');
    if (ch === 'cyber' || ch === 'ai') {
      state.chapter = ch;
    }
  }

  function updateUrlParams() {
    const params = new URLSearchParams(window.location.search);
    params.set('chapter', state.chapter);
    if (state.currentEditionData && state.currentEditionData.metadata) {
      params.set('date', state.currentEditionData.metadata.date);
    }
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, '', newUrl);
  }

  function setupEventListeners() {
    el.tabAi.addEventListener('click', () => switchChapter('ai'));
    el.tabCyber.addEventListener('click', () => switchChapter('cyber'));

    el.editionSelect.addEventListener('change', (e) => {
      const selectedFile = e.target.value;
      loadEdition(selectedFile);
    });

    el.searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value.toLowerCase().trim();
      renderContent();
    });

    el.btnCopyMd.addEventListener('click', () => {
      if (!state.currentEditionData || !state.currentEditionData.markdown) return;
      navigator.clipboard.writeText(state.currentEditionData.markdown).then(() => {
        showToast('Semantic Markdown copied to clipboard!');
      });
    });

    el.btnCopyJson.addEventListener('click', () => {
      if (!state.currentEditionData) return;
      const jsonStr = JSON.stringify(state.currentEditionData, null, 2);
      navigator.clipboard.writeText(jsonStr).then(() => {
        showToast('Machine-readable JSON copied to clipboard!');
      });
    });

    el.btnTheme.addEventListener('click', () => {
      state.theme = state.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('bb-theme', state.theme);
      applyTheme(state.theme);
    });
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    el.btnTheme.textContent = theme === 'dark' ? '☀️' : '🌙';
  }

  function switchChapter(chap) {
    if (state.chapter === chap) return;
    state.chapter = chap;
    updateChapterStyles();
    updateEditionDropdown();
    loadEdition();
  }

  function updateChapterStyles() {
    if (state.chapter === 'cyber') {
      document.body.classList.add('cyber-mode');
      el.brand.classList.add('cyber-active');
      el.tabCyber.classList.add('active');
      el.tabAi.classList.remove('active');
      el.heroDesc.textContent = state.indexData.chapters.cyber.tagline;
    } else {
      document.body.classList.remove('cyber-mode');
      el.brand.classList.remove('cyber-active');
      el.tabAi.classList.add('active');
      el.tabCyber.classList.remove('active');
      el.heroDesc.textContent = state.indexData.chapters.ai.tagline;
    }
  }

  function updateEditionDropdown() {
    const chapterConfig = state.indexData.chapters[state.chapter];
    el.editionSelect.innerHTML = '';

    chapterConfig.editions.forEach((ed, idx) => {
      const opt = document.createElement('option');
      opt.value = ed.file;
      opt.textContent = `${ed.date} ${idx === 0 ? '(Latest)' : ''}`;
      el.editionSelect.appendChild(opt);
    });
  }

  async function loadEdition(fileUrl = null) {
    const chapterConfig = state.indexData.chapters[state.chapter];
    const targetFile = fileUrl || chapterConfig.latest_file;

    try {
      const resp = await fetch(targetFile);
      if (resp.ok) {
        state.currentEditionData = await resp.json();
      } else {
        throw new Error(`Failed to load ${targetFile}`);
      }
    } catch (e) {
      console.warn('Fetch failed, checking embedded fallback...', e);
      const fallbackId = `initial-${state.chapter}-latest`;
      const fallbackEl = document.getElementById(fallbackId);
      if (fallbackEl) {
        state.currentEditionData = JSON.parse(fallbackEl.textContent);
      }
    }

    updateUrlParams();
    renderPage();
  }

  function renderPage() {
    if (!state.currentEditionData) return;
    const data = state.currentEditionData;
    const meta = data.metadata || {};

    updateChapterStyles();

    // Hero metadata
    el.heroTitle.textContent = meta.edition_title || 'Daily Technical Intelligence';
    el.badgeDate.textContent = meta.date || 'Today';
    el.badgeAudience.textContent = meta.target_audience || 'Engineering Teams';

    if (state.indexData.generated_at) {
      const d = new Date(state.indexData.generated_at);
      el.lastSyncedTime.textContent = d.toLocaleDateString(undefined, {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
      });
    }

    // 30-Min Priority Sprint Banner
    const sprint = meta.high_leverage_30_min_pick;
    if (sprint && sprint.title) {
      el.prioritySprint.style.display = 'flex';
      const urlHtml = sprint.url 
        ? `<a href="${escapeHtml(sprint.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(sprint.title)} ↗</a>` 
        : escapeHtml(sprint.title);
      el.prioritySprint.innerHTML = `
        <div class="priority-icon">⭐</div>
        <div class="priority-content">
          <div class="priority-label">30-Minute Priority Sprint</div>
          <div class="priority-title">${urlHtml}</div>
          <div class="priority-rationale">${escapeHtml(sprint.rationale || '')}</div>
        </div>
      `;
    } else {
      el.prioritySprint.style.display = 'none';
    }

    // 5-Min Executive Briefing
    const takeaways = meta.quick_takeaway_5_min || [];
    if (takeaways.length > 0) {
      el.briefingBox.style.display = 'block';
      el.briefingList.innerHTML = takeaways.map(t => `
        <li class="briefing-item">
          <span class="briefing-bullet">›</span>
          <span>${formatInlineLinks(t)}</span>
        </li>
      `).join('');
    } else {
      el.briefingBox.style.display = 'none';
    }

    // Pillar Navigation
    renderPillarNav(data.topics || []);

    // Render topics / cards
    renderContent();
  }

  function renderPillarNav(topics) {
    el.pillarNav.innerHTML = topics.map(t => `
      <a href="#${t.topic_id}" class="pillar-pill">
        <span>${escapeHtml(t.topic_title.split(' ')[0] || '•')}</span>
        <span>${escapeHtml(t.topic_title.replace(/^[0-9\.\s]+/, ''))}</span>
      </a>
    `).join('');
  }

  function renderContent() {
    const topics = state.currentEditionData.topics || [];
    const query = state.searchQuery;

    let html = '';

    topics.forEach(topic => {
      // Filter subtopics if search active
      const filteredSubs = (topic.subtopics || []).filter(sub => {
        if (!query) return true;
        const text = (sub.title + ' ' + (sub.summary || '') + ' ' + JSON.stringify(sub.details || {})).toLowerCase();
        return text.includes(query);
      });

      if (filteredSubs.length === 0 && query) return;

      html += `
        <section id="${topic.topic_id}" class="section-pillar">
          <div class="pillar-header">
            <h2 class="pillar-title">${escapeHtml(topic.topic_title)}</h2>
          </div>
          <div class="cards-grid">
            ${filteredSubs.map(sub => renderSubtopicCard(sub, topic.topic_id)).join('')}
          </div>
        </section>
      `;
    });

    if (!html && query) {
      html = `<div style="text-align: center; padding: 4rem 1rem; color: var(--text-muted);">
        No items matched "<strong>${escapeHtml(query)}</strong>". Try another keyword or clear search.
      </div>`;
    }

    el.contentArea.innerHTML = html;
  }

  function renderSubtopicCard(sub, topicId) {
    // Check if Concept of the Day (3-tier)
    if (topicId === 'concept-of-the-day' || sub.details['Simple Explanation (Beginner)'] || sub.tier_1_mental_model) {
      return renderConceptCard(sub);
    }

    // Check if 60-90 min Action plan
    if (topicId === 'actionable-learning-plan' || sub.details['0–20 min']) {
      return renderActionPlanCard(sub);
    }

    const titleHtml = sub.url || sub.primary_url
      ? `<a href="${escapeHtml(sub.url || sub.primary_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(sub.title)} ↗</a>`
      : escapeHtml(sub.title);

    let detailsHtml = '';
    const details = sub.details || {};

    // Special pill for CVSS / Exploit status in cyber
    let badgeHtml = '';
    if (details['Impact Vector'] && details['Impact Vector'].text.includes('CVSS Score: 10')) {
      badgeHtml += `<span class="severity-pill sev-critical">CVSS 10.0 CRITICAL</span> `;
    } else if (details['Impact Vector'] && details['Impact Vector'].text.includes('CVSS')) {
      badgeHtml += `<span class="severity-pill sev-high">HIGH SEVERITY</span> `;
    }

    if (details['Exploitation Status'] && details['Exploitation Status'].text.toLowerCase().includes('in the wild')) {
      badgeHtml += `<span class="severity-pill sev-critical" style="margin-left: 0.3rem;">EXPLOITED IN WILD</span>`;
    }

    const detailKeys = Object.keys(details).filter(k => k !== 'bullets');
    if (detailKeys.length > 0) {
      detailsHtml = `
        <div class="details-list">
          ${detailKeys.map(k => {
            const item = details[k];
            let valText = typeof item === 'object' ? item.text : item;
            let linksHtml = '';
            if (item && item.links && item.links.length > 0) {
              linksHtml = ' ' + item.links.map(l => `<a href="${escapeHtml(l.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(l.name || 'Source')} ↗</a>`).join(' · ');
            }
            return `
              <div class="detail-row">
                <span class="detail-label">${escapeHtml(k)}</span>
                <span class="detail-value">${escapeHtml(valText)}${linksHtml}</span>
              </div>
            `;
          }).join('')}
        </div>
      `;
    }

    // Bullets if present
    let bulletsHtml = '';
    const bullets = details.bullets || sub.bullets || [];
    if (bullets.length > 0) {
      bulletsHtml = `
        <ul style="padding-left: 1.25rem; color: var(--text-muted); font-size: 0.875rem; margin-top: 0.5rem; display: grid; gap: 0.35rem;">
          ${bullets.map(b => {
            const bText = typeof b === 'object' ? b.text : b;
            return `<li>${formatInlineLinks(bText)}</li>`;
          }).join('')}
        </ul>
      `;
    }

    return `
      <article class="intel-card">
        <div class="card-top">
          <h3 class="card-title">${titleHtml}</h3>
          <div>${badgeHtml}</div>
        </div>
        ${sub.summary ? `<div class="card-summary">${formatInlineLinks(sub.summary)}</div>` : ''}
        ${detailsHtml}
        ${bulletsHtml}
      </article>
    `;
  }

  function renderConceptCard(sub) {
    const details = sub.details || {};
    const t1 = details['Simple Explanation (Beginner)']?.text || details['Mental Model (Beginner Intuition)']?.text || sub.tier_1_mental_model || '';
    const t2 = details['Mechanics & Architecture']?.text || details['Detailed Architecture']?.text || sub.tier_2_technical_mechanics || '';
    const t3 = details['Production Implementation']?.text || details['Production Pattern']?.text || sub.tier_3_production_pattern || '';

    return `
      <article class="intel-card">
        <h3 class="card-title">${escapeHtml(sub.title)}</h3>
        <div class="concept-container">
          <div class="tier-card tier-1">
            <div class="tier-header">
              <span class="tier-tag">Tier 1 • Mental Model</span>
            </div>
            <div class="tier-body">${escapeHtml(t1 || 'Intuitive foundation.')}</div>
          </div>
          <div class="tier-card tier-2">
            <div class="tier-header">
              <span class="tier-tag">Tier 2 • Systems Architecture</span>
            </div>
            <div class="tier-body">${escapeHtml(t2 || 'Mechanics & technical breakdown.')}</div>
          </div>
          <div class="tier-card tier-3">
            <div class="tier-header">
              <span class="tier-tag">Tier 3 • Production Pattern</span>
            </div>
            <div class="tier-body">${escapeHtml(t3 || 'Tradeoffs & code implementation.')}</div>
          </div>
        </div>
      </article>
    `;
  }

  function renderActionPlanCard(sub) {
    const details = sub.details || {};
    const phases = [
      { time: '0–20 min', text: details['0–20 min']?.text || 'High-signal reading & video review' },
      { time: '20–50 min', text: details['20–50 min']?.text || 'Core theoretical mechanics' },
      { time: '50–90 min', text: details['50–90 min']?.text || 'Hands-on code prototype & local benchmark' }
    ];

    return `
      <article class="intel-card">
        <h3 class="card-title">${escapeHtml(sub.title || 'Structured 60–90 Min Action Plan')}</h3>
        <div class="learning-plan-grid" style="margin-top: 0.75rem;">
          ${phases.map(p => `
            <div class="plan-phase">
              <div class="plan-time">⏱️ ${escapeHtml(p.time)}</div>
              <div class="plan-text">${escapeHtml(p.text)}</div>
            </div>
          `).join('')}
        </div>
      </article>
    `;
  }

  function showToast(msg) {
    el.toast.textContent = msg;
    el.toast.classList.add('show');
    setTimeout(() => {
      el.toast.classList.remove('show');
    }, 2800);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, m => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[m]);
  }

  function formatInlineLinks(str) {
    if (!str) return '';
    const escaped = escapeHtml(str);
    // Convert (arXiv:XXXX.XXXX) or URLs to links
    return escaped.replace(/(https?:\/\/[^\s\)]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1 ↗</a>');
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
