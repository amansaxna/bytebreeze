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
  <title>ByteBreeze — Daily Technical Intelligence & AI Engineering Digest</title>
  <meta name="description" content="High-signal daily intelligence briefing tailored for software engineers leveling up in AI/ML systems and cybersecurity engineering.">
  
  <!-- Favicon -->
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220%22 width=%22100%22 height=%22100%22><text y=%22.9em%22 font-size=%2290%22>⚡</text></svg>">
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- Header -->
  <header class="site-header">
    <div class="container header-inner">
      <a href="./" class="brand">
        <div class="brand-logo">⚡</div>
        <div class="brand-text">
          <span class="brand-title">ByteBreeze</span>
          <span class="brand-tagline">Daily Technical Intel</span>
        </div>
      </a>

      <!-- Chapter Navigation -->
      <nav class="chapter-tabs" aria-label="Intelligence Chapters">
        <button id="tab-ai" class="tab-btn ai-tab active" type="button">
          <span>🤖</span> AI Engineering
        </button>
        <button id="tab-cyber" class="tab-btn cyber-tab" type="button">
          <span>🛡️</span> Cybersecurity Intel
        </button>
      </nav>

      <!-- Utility Actions -->
      <div class="header-actions">
        <div class="edition-select-wrap">
          <select id="edition-select" class="select-custom" aria-label="Select Briefing Edition"></select>
        </div>
        <button id="btn-copy-md" class="action-btn" title="Copy Semantic Markdown for Notes/LLM" type="button">
          📋 Markdown
        </button>
        <button id="btn-copy-json" class="action-btn" title="Copy Machine-Readable JSON" type="button">
          {{"}} JSON
        </button>
        <button id="btn-theme" class="action-btn" title="Toggle Dark/Light Mode" type="button">
          ☀️
        </button>
      </div>
    </div>
  </header>

  <!-- Main Hero -->
  <main class="container">
    <section class="hero-section">
      <div class="hero-glow"></div>
      
      <div class="hero-meta-row">
        <span class="badge badge-live">Live Sync</span>
        <span id="badge-date" class="badge badge-date">Loading...</span>
        <span id="badge-audience" class="badge badge-audience">Software Engineers</span>
      </div>

      <h1 id="hero-title" class="hero-title">Daily Technical Intelligence</h1>
      <p id="hero-desc" class="hero-desc">
        High-signal intelligence gathered, synthesized, and structured for production systems builders.
      </p>

      <!-- 30-Minute Priority Sprint Card -->
      <div id="priority-sprint" class="priority-sprint" style="display: none;"></div>

      <!-- 5-Minute Executive Briefing -->
      <div id="briefing-box" class="briefing-box">
        <div class="briefing-header">
          <div class="briefing-heading">
            <span>🔥</span> 5-Minute Executive Briefing
          </div>
        </div>
        <ul id="briefing-list" class="briefing-list"></ul>
      </div>

      <!-- Quick Jump Pillar Nav -->
      <nav id="pillar-nav" class="pillar-nav" aria-label="Core Pillars Navigation"></nav>

      <!-- Search & Filter Bar -->
      <div class="search-bar-wrap">
        <input 
          id="search-input" 
          type="search" 
          class="search-input" 
          placeholder="🔍 Search breakthroughs, CVEs, GitHub repositories, mental models, or authors..."
          aria-label="Filter intelligence items"
        >
      </div>
    </section>

    <!-- Content Pillars -->
    <div id="content-area"></div>
  </main>

  <!-- Footer -->
  <footer class="site-footer">
    <div class="container footer-inner">
      <div>
        <strong>ByteBreeze</strong> — Autonomous Technical Intelligence Pipeline. Updated daily at 8:30 AM IST.
        <div style="font-size: 0.75rem; margin-top: 0.25rem;">
          Last synced: <span id="last-synced-time">Recently</span>
        </div>
      </div>
      <div class="footer-links">
        <a href="https://github.com/amansaxna/bytebreeze" target="_blank" rel="noopener noreferrer">GitHub Repo</a>
        <a href="https://docs.google.com/document/d/e/2PACX-1vQhw17LLem50H4hn6f_TJRCzFo6r3ec_KgBFFYZcgUMYnjLS8tQqiCem42xrLGj2w0BNxE5o5wkv5xq/pub" target="_blank" rel="noopener noreferrer">AI Doc</a>
        <a href="https://docs.google.com/document/d/e/2PACX-1vQsdpeQlhfXV47otThYdbFlqb2GnQBrtMga4mmZxo2EvNQUhMqVlS4ATgMzKpTAxXyg3WN6eBKfSNLh/pub" target="_blank" rel="noopener noreferrer">Cyber Doc</a>
      </div>
    </div>
  </footer>

  <!-- Toast Notification -->
  <div id="toast" class="toast">Copied to clipboard!</div>

  <!-- Inline Initial Data for Instant Hydration (Works even without local server) -->
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
