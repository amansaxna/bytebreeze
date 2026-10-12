import os
import json

def render_index_html():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(root_dir, "data")
    
    with open(os.path.join(data_dir, "index.json"), "r", encoding="utf-8") as f:
        index_json = f.read()

    with open(os.path.join(data_dir, "ai", "latest.json"), "r", encoding="utf-8") as f:
        ai_json = f.read()

    with open(os.path.join(data_dir, "cyber", "latest.json"), "r", encoding="utf-8") as f:
        cyber_json = f.read()

    html_template = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ByteBreeze — Daily Technical Intelligence for AI & Cybersecurity Systems</title>
  <meta name="description" content="High-signal daily intelligence briefing tailored specifically for software engineers leveling up in AI/ML systems and cybersecurity engineering.">
  
  <!-- Favicon -->
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 rx=%2222%22 fill=%22%2307090e%22/><path d=%22M56 18L26 56h20l-8 26 36-40H52l8-24z%22 fill=%22%2306b6d4%22/></svg>">
  
  <!-- Typography: Geist & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- Ambient Dot Matrix Background -->
  <div class="dot-matrix" aria-hidden="true"></div>

  <!-- Sticky Global Navigation Bar -->
  <header class="site-header">
    <div class="container header-inner">
      <a href="./" class="brand">
        <div class="brand-glyph">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
          </svg>
        </div>
        <div class="brand-meta">
          <span class="brand-title">ByteBreeze</span>
          <span class="brand-sub">Daily Technical Intel</span>
        </div>
      </a>

      <!-- Chapter Segmented Control -->
      <nav class="chapter-nav" aria-label="Intelligence Chapters">
        <button id="tab-ai" class="chapter-btn active" type="button">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2a4 4 0 0 1 4 4v1a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4zM6 14a6 6 0 0 1 12 0v2H6v-2zM4 22h16"></path>
          </svg>
          AI Systems
        </button>
        <button id="tab-cyber" class="chapter-btn" type="button">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          Cybersecurity Intel
        </button>
      </nav>

      <!-- Utility Actions -->
      <div class="header-actions">
        <div class="edition-select-wrap">
          <select id="edition-select" class="select-edition" aria-label="Select Intelligence Edition"></select>
          <span class="select-arrow">▼</span>
        </div>
        <button id="btn-copy-md" class="btn-ctrl" title="Copy Semantic Markdown" type="button">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
          MD
        </button>
        <button id="btn-copy-json" class="btn-ctrl" title="Copy Machine-Readable JSON" type="button">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
          JSON
        </button>
        <button id="btn-theme" class="btn-ctrl" title="Toggle Theme" type="button" aria-label="Toggle Theme">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Intelligence Surface -->
  <main class="container">
    <section class="hero-hub">
      <div class="hero-ambient-glow" aria-hidden="true"></div>
      
      <div class="hero-header-row">
        <span class="meta-chip meta-chip-live">
          <span class="pulse-node"></span>
          PIPELINE SYNCED
        </span>
        <span id="badge-date" class="meta-chip">Loading...</span>
        <span id="badge-audience" class="meta-chip">Systems Engineers</span>
      </div>

      <h1 id="hero-title" class="hero-headline">Daily Technical Intelligence</h1>
      <p id="hero-desc" class="hero-subtitle">
        High-signal technical intelligence gathered, evaluated, and structured for production systems engineers.
      </p>

      <!-- 30-Minute Priority Sprint Card -->
      <div id="priority-sprint" class="sprint-spotlight" style="display: none;"></div>

      <!-- 5-Minute Executive Briefing Matrix -->
      <div id="briefing-box" class="briefing-matrix">
        <div class="briefing-matrix-header">
          <div class="matrix-title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
            5-Minute Executive Briefing
          </div>
        </div>
        <ul id="briefing-list" class="matrix-grid"></ul>
      </div>

      <!-- Pillar Quick Navigation Dock -->
      <nav id="pillar-nav" class="pillar-dock" aria-label="Core Pillars Navigation"></nav>

      <!-- Real-Time Filter Hub -->
      <div class="filter-hub">
        <span class="search-icon-slot">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </span>
        <input 
          id="search-input" 
          type="search" 
          class="search-field" 
          placeholder="Filter breakthroughs, CVEs, GitHub repositories, systems concepts, or authors..."
          aria-label="Filter intelligence records"
        >
      </div>
    </section>

    <!-- Content Pillars -->
    <div id="content-area"></div>
  </main>

  <!-- Footer -->
  <footer class="site-footer">
    <div class="container footer-layout">
      <div>
        <strong>ByteBreeze</strong> — Autonomous Intelligence Pipeline. Synchronized daily at 8:30 AM IST.
        <div style="font-size: 0.76rem; margin-top: 0.35rem; font-family: var(--font-mono); color: var(--text-dim);">
          Latest data sync: <span id="last-synced-time">Active</span>
        </div>
      </div>
      <nav class="footer-nav">
        <a href="https://github.com/amansaxna/bytebreeze" target="_blank" rel="noopener noreferrer">Source Code ↗</a>
        <a href="https://docs.google.com/document/d/e/2PACX-1vQhw17LLem50H4hn6f_TJRCzFo6r3ec_KgBFFYZcgUMYnjLS8tQqiCem42xrLGj2w0BNxE5o5wkv5xq/pub" target="_blank" rel="noopener noreferrer">AI Doc ↗</a>
        <a href="https://docs.google.com/document/d/e/2PACX-1vQsdpeQlhfXV47otThYdbFlqb2GnQBrtMga4mmZxo2EvNQUhMqVlS4ATgMzKpTAxXyg3WN6eBKfSNLh/pub" target="_blank" rel="noopener noreferrer">Cyber Doc ↗</a>
      </nav>
    </div>
  </footer>

  <!-- Toast Notice -->
  <div id="toast" class="toast-notice" role="status" aria-live="polite">Copied to clipboard</div>

  <!-- Pre-baked Embedded State for Zero-Latency Initial Render -->
  <script id="initial-index-data" type="application/json">{index_json}</script>
  <script id="initial-ai-latest" type="application/json">{ai_json}</script>
  <script id="initial-cyber-latest" type="application/json">{cyber_json}</script>

  <script src="app.js"></script>
</body>
</html>
"""
    index_path = os.path.join(root_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Generated index.html at {index_path}")

if __name__ == "__main__":
    render_index_html()
