// ByteBreeze Frontend Application Controller — Anti-Slop High-Signal Engine
(function() {
  'use strict';

  // Global state
  const state = {
    chapter: 'ai', // 'ai' | 'cyber'
    indexData: null,
    currentEditionData: null,
    searchQuery: '',
    theme: localStorage.getItem('bb-theme') || 'dark',
    activeTopicId: null
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
    readtimeVal: document.getElementById('readtime-val'),
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
    setupKeyboardShortcuts();

    // 1. Load initial embedded data if present
    try {
      const embedded = document.getElementById('initial-index-data');
      if (embedded && embedded.textContent.trim()) {
        state.indexData = JSON.parse(embedded.textContent);
      }
    } catch (e) {
      console.warn('Initial embedded index parse fallback:', e);
    }

    // 2. Fetch live data/index.json if available
    try {
      const resp = await fetch('data/index.json');
      if (resp.ok) {
        state.indexData = await resp.json();
      }
    } catch (e) {
      console.log('Serving from embedded index state:', e);
    }

    if (!state.indexData) {
      console.error('Failed to load ByteBreeze index catalog.');
      return;
    }

    updateEditionDropdown();
    await loadEdition();
    setupScrollSpy();
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
        showToast('Semantic Markdown copied to clipboard');
      });
    });

    el.btnCopyJson.addEventListener('click', () => {
      if (!state.currentEditionData) return;
      const jsonStr = JSON.stringify(state.currentEditionData, null, 2);
      navigator.clipboard.writeText(jsonStr).then(() => {
        showToast('Machine-readable JSON copied to clipboard');
      });
    });

    el.btnTheme.addEventListener('click', () => {
      state.theme = state.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('bb-theme', state.theme);
      applyTheme(state.theme);
    });

    // Delegated click for deep-dive drawers
    el.contentArea.addEventListener('click', (e) => {
      const toggle = e.target.closest('.deep-dive-toggle');
      if (toggle) {
        const item = toggle.closest('.intel-item');
        if (item) {
          item.classList.toggle('expanded');
          const isExp = item.classList.contains('expanded');
          toggle.querySelector('.deep-dive-label').textContent = isExp ? 'Collapse Technical Breakdown' : 'Expand Technical Breakdown';
        }
      }
    });
  }

  function setupKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
      // Ignore if user is already typing in an input
      const tag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
      if (tag === 'input' || tag === 'textarea' || tag === 'select') {
        if (e.key === 'Escape') {
          document.activeElement.blur();
          state.searchQuery = '';
          el.searchInput.value = '';
          renderContent();
        }
        return;
      }

      if (e.key === '/' || e.key === 's') {
        e.preventDefault();
        el.searchInput.focus();
        el.searchInput.select();
      } else if (e.key === '1') {
        e.preventDefault();
        switchChapter('ai');
      } else if (e.key === '2') {
        e.preventDefault();
        switchChapter('cyber');
      } else if (e.key.toLowerCase() === 't') {
        e.preventDefault();
        el.btnTheme.click();
      }
    });
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    el.btnTheme.innerHTML = theme === 'dark' 
      ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>` 
      : `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
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
      el.tabCyber.classList.add('active');
      el.tabAi.classList.remove('active');
      el.heroDesc.textContent = state.indexData.chapters.cyber.tagline;
    } else {
      document.body.classList.remove('cyber-mode');
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
      console.warn('Network fetch unavailable, using embedded fallback state:', e);
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

    // Hero Meta
    el.heroTitle.textContent = meta.edition_title || 'Daily Technical Intelligence';
    el.badgeDate.textContent = meta.date || 'Today';
    el.badgeAudience.textContent = meta.target_audience || 'Systems Engineers';

    // Calculate dynamic reading time
    const rawWordCount = JSON.stringify(data).split(/\s+/).length;
    const minutes = Math.max(4, Math.round(rawWordCount / 260));
    if (el.readtimeVal) {
      el.readtimeVal.textContent = `${minutes} MIN READ`;
    }

    if (state.indexData.generated_at) {
      const d = new Date(state.indexData.generated_at);
      el.lastSyncedTime.textContent = d.toLocaleDateString(undefined, {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
      });
    }

    // 30-Minute Priority Sprint Card
    const sprint = meta.high_leverage_30_min_pick;
    if (sprint && sprint.title) {
      el.prioritySprint.style.display = 'grid';
      const cleanUrl = sprint.url || '#';
      el.prioritySprint.innerHTML = `
        <div class="sprint-badge-cell">
          <div class="sprint-time">30</div>
          <div class="sprint-unit">Min</div>
        </div>
        <div class="sprint-content">
          <div class="sprint-eyebrow">Priority High-Leverage Sprint</div>
          <div class="sprint-title">${escapeHtml(sprint.title)}</div>
          <div class="sprint-rationale">${escapeHtml(sprint.rationale || '')}</div>
        </div>
        ${sprint.url ? `
          <div>
            <a href="${escapeHtml(cleanUrl)}" target="_blank" rel="noopener noreferrer" class="sprint-action-btn">
              Direct Primary Link
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg>
            </a>
          </div>
        ` : ''}
      `;
    } else {
      el.prioritySprint.style.display = 'none';
    }

    // 5-Min Executive Briefing Matrix
    const takeaways = meta.quick_takeaway_5_min || [];
    if (takeaways.length > 0) {
      el.briefingBox.style.display = 'block';
      el.briefingList.innerHTML = takeaways.map((t, i) => `
        <li class="matrix-card">
          <span class="matrix-index">0${i + 1}</span>
          <div class="matrix-text">${formatInlineLinks(t)}</div>
        </li>
      `).join('');
    } else {
      el.briefingBox.style.display = 'none';
    }

    // Pillar Navigation
    renderPillarNav(data.topics || []);

    // Render Topics & Cards
    renderContent();
    setupScrollSpy();
  }

  function renderPillarNav(topics) {
    el.pillarNav.innerHTML = topics.map((t, i) => {
      const cleanLabel = t.topic_title.replace(/^[0-9\.\s]+/, '').replace(/^[\uD800-\uDBFF\uDC00-\uDFFF\u2600-\u27BF]+\s*/, '');
      const activeClass = i === 0 ? 'active' : '';
      return `
        <a href="#${t.topic_id}" class="dock-pill ${activeClass}" data-target="${t.topic_id}">
          <span>${escapeHtml(cleanLabel)}</span>
        </a>
      `;
    }).join('');
  }

  function renderContent() {
    const topics = state.currentEditionData.topics || [];
    const query = state.searchQuery;

    let html = '';

    topics.forEach((topic, idx) => {
      const filteredSubs = (topic.subtopics || []).filter(sub => {
        if (!query) return true;
        const text = (sub.title + ' ' + (sub.summary || '') + ' ' + JSON.stringify(sub.details || {})).toLowerCase();
        return text.includes(query);
      });

      if (filteredSubs.length === 0 && query) return;

      const cleanHeading = topic.topic_title.replace(/^[0-9\.\s]+/, '').replace(/^[\uD800-\uDBFF\uDC00-\uDFFF\u2600-\u27BF]+\s*/, '');

      html += `
        <section id="${topic.topic_id}" class="intel-section">
          <div class="section-head">
            <div class="section-head-left">
              <span class="section-num">0${idx + 1}</span>
              <h2 class="section-heading">${escapeHtml(cleanHeading)}</h2>
            </div>
          </div>
          <div class="cards-matrix">
            ${filteredSubs.map(sub => renderSubtopicCard(sub, topic.topic_id)).join('')}
          </div>
        </section>
      `;
    });

    if (!html && query) {
      html = `<div style="text-align: center; padding: 5rem 1rem; color: var(--text-muted); font-family: var(--font-mono);">
        No intelligence records matching "<strong>${escapeHtml(query)}</strong>". Press <kbd class="footer-kbd">Esc</kbd> to clear.
      </div>`;
    }

    el.contentArea.innerHTML = html;
  }

  function renderSubtopicCard(sub, topicId) {
    // 1. Concept of the Day (3-Tier View)
    if (topicId === 'concept-of-the-day' || sub.details['Simple Explanation (Beginner)'] || sub.tier_1_mental_model) {
      return renderConceptCard(sub);
    }

    // 2. 60-90 Minute Learning Plan (Phased Timeline)
    if (topicId === 'actionable-learning-plan' || sub.details['0–20 min']) {
      return renderActionPlanCard(sub);
    }

    const titleLink = sub.url || sub.primary_url;
    const titleHtml = titleLink
      ? `<a href="${escapeHtml(titleLink)}" target="_blank" rel="noopener noreferrer">${escapeHtml(sub.title)} <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg></a>`
      : escapeHtml(sub.title);

    let badgeHtml = '';
    const details = sub.details || {};

    // CVSS Score & Wild Exploitation badges
    if (details['Impact Vector'] && details['Impact Vector'].text.includes('CVSS Score: 10')) {
      badgeHtml += `<span class="badge-sev badge-sev-critical">CVSS 10.0 CRITICAL</span> `;
    } else if (details['Impact Vector'] && details['Impact Vector'].text.includes('CVSS')) {
      badgeHtml += `<span class="badge-sev badge-sev-high">HIGH SEVERITY</span> `;
    }

    if (details['Exploitation Status'] && details['Exploitation Status'].text.toLowerCase().includes('in the wild')) {
      badgeHtml += `<span class="badge-sev badge-sev-critical">ACTIVE IN WILD</span>`;
    }

    // Spec ledger (Key-Value)
    let ledgerHtml = '';
    const detailKeys = Object.keys(details).filter(k => k !== 'bullets');
    if (detailKeys.length > 0) {
      ledgerHtml = `
        <div class="spec-ledger">
          ${detailKeys.map(k => {
            const item = details[k];
            let valText = typeof item === 'object' ? item.text : item;
            let linksHtml = '';
            if (item && item.links && item.links.length > 0) {
              linksHtml = ' ' + item.links.map(l => `<a href="${escapeHtml(l.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(l.name || 'Canonical Link')} ↗</a>`).join(' · ');
            }
            return `
              <div class="ledger-entry">
                <span class="ledger-key">${escapeHtml(k)}</span>
                <span class="ledger-val">${escapeHtml(valText)}${linksHtml}</span>
              </div>
            `;
          }).join('')}
        </div>
      `;
    }

    // Bullets list
    let bulletsHtml = '';
    const bullets = details.bullets || sub.bullets || [];
    if (bullets.length > 0) {
      bulletsHtml = `
        <ul class="item-bullets">
          ${bullets.map(b => {
            const bText = typeof b === 'object' ? b.text : b;
            return `<li>${formatInlineLinks(bText)}</li>`;
          }).join('')}
        </ul>
      `;
    }

    const hasExtraDetails = ledgerHtml || bulletsHtml;

    return `
      <article class="intel-item">
        <div class="item-top-row">
          <h3 class="item-title">${titleHtml}</h3>
          <div>${badgeHtml}</div>
        </div>
        ${sub.summary ? `<div class="item-summary">${formatInlineLinks(sub.summary)}</div>` : ''}
        ${hasExtraDetails ? `
          <button class="deep-dive-toggle" type="button" aria-expanded="false">
            <span class="deep-dive-label">Expand Technical Breakdown</span>
            <svg class="deep-dive-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </button>
          <div class="deep-dive-drawer">
            ${ledgerHtml}
            ${bulletsHtml}
          </div>
        ` : ''}
      </article>
    `;
  }

  function renderConceptCard(sub) {
    const details = sub.details || {};
    const t1 = details['Simple Explanation (Beginner)']?.text || details['Mental Model (Beginner Intuition)']?.text || sub.tier_1_mental_model || '';
    const t2 = details['Mechanics & Architecture']?.text || details['Detailed Architecture']?.text || sub.tier_2_technical_mechanics || '';
    const t3 = details['Production Implementation']?.text || details['Production Pattern']?.text || sub.tier_3_production_pattern || '';

    return `
      <article class="intel-item">
        <h3 class="item-title">${escapeHtml(sub.title)}</h3>
        <div class="concept-grid">
          <div class="concept-tier-card tier-t1">
            <div class="tier-indicator">
              <span class="tier-chip">Tier 1 • Mental Model</span>
            </div>
            <div class="tier-text">${escapeHtml(t1 || 'Foundational conceptual model.')}</div>
          </div>
          <div class="concept-tier-card tier-t2">
            <div class="tier-indicator">
              <span class="tier-chip">Tier 2 • Systems Mechanics</span>
            </div>
            <div class="tier-text">${escapeHtml(t2 || 'Internal architecture breakdown.')}</div>
          </div>
          <div class="concept-tier-card tier-t3">
            <div class="tier-indicator">
              <span class="tier-chip">Tier 3 • Production Code Pattern</span>
            </div>
            <div class="tier-text">${escapeHtml(t3 || 'Production tradeoffs and implementation safeguards.')}</div>
          </div>
        </div>
      </article>
    `;
  }

  function renderActionPlanCard(sub) {
    const details = sub.details || {};
    const phases = [
      { time: '0–20 min', label: 'Theory / Read', text: details['0–20 min']?.text || 'High-signal reading & canonical paper review' },
      { time: '20–50 min', label: 'Mechanics', text: details['20–50 min']?.text || 'Core theoretical breakdown and architecture diagram' },
      { time: '50–90 min', label: 'Hands-On Build', text: details['50–90 min']?.text || 'Code prototype or reproducible local benchmark' }
    ];

    return `
      <article class="intel-item">
        <h3 class="item-title">${escapeHtml(sub.title || 'Structured 60–90 Min Action Plan')}</h3>
        <div class="action-plan-track">
          ${phases.map(p => `
            <div class="action-step-card">
              <div class="action-time-badge">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                ${escapeHtml(p.time)} • ${escapeHtml(p.label)}
              </div>
              <div class="action-desc">${formatInlineLinks(p.text)}</div>
            </div>
          `).join('')}
        </div>
      </article>
    `;
  }

  // ScrollSpy with IntersectionObserver
  function setupScrollSpy() {
    const sections = document.querySelectorAll('.intel-section');
    if (!sections.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          document.querySelectorAll('.dock-pill').forEach(pill => {
            if (pill.getAttribute('data-target') === id) {
              pill.classList.add('active');
              pill.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
            } else {
              pill.classList.remove('active');
            }
          });
        }
      });
    }, {
      rootMargin: '-20% 0px -65% 0px'
    });

    sections.forEach(sec => observer.observe(sec));
  }

  function showToast(msg) {
    el.toast.textContent = msg;
    el.toast.classList.add('visible');
    setTimeout(() => {
      el.toast.classList.remove('visible');
    }, 2400);
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
    return escaped.replace(/(https?:\/\/[^\s\)]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1 ↗</a>');
  }

  // Self execute
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
