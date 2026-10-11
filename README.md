# ⚡ ByteBreeze (Daily Technical Intelligence)

> **High-signal daily intelligence briefing tailored for software engineers leveling up in AI/ML systems and cybersecurity engineering.**

Hosted repository: [`git@github.com:amansaxna/bytebreeze.git`](https://github.com/amansaxna/bytebreeze)

---

## 🧭 Mission & Chapters

ByteBreeze gathers, filters, synthesizes, and presents production-grade intelligence across two specialized engineering tracks:

1. **🤖 AI Engineering Chapter**:
   - Tailored for backend and systems engineers transitioning to LLM architectures, model serving, inference engines, test-time compute, and RAG.
   - 8 Research Pillars: Research Papers & Benchmarks, Practitioners to Follow, High-Engagement Technical Discussions, YouTube Video Breakdowns, Open-Source Tools & Frameworks, 3-Tier Progressive Concept of the Day, Structured 60–90 Min Learning Plan, and Career Relevance.
   - Synchronized from: [Daily AI Engineering Learning Digest](https://docs.google.com/document/d/e/2PACX-1vQhw17LLem50H4hn6f_TJRCzFo6r3ec_KgBFFYZcgUMYnjLS8tQqiCem42xrLGj2w0BNxE5o5wkv5xq/pub)

2. **🛡️ Cybersecurity Intel Chapter**:
   - Zero-days, weaponized exploits, AppSec architectural patterns, academic security research primitives, high-signal podcasts, and geopolitical threat actor campaigns.
   - 5 Threat Pillars: Critical Zero-Days (CVSS score, root cause, in-the-wild exploitation status, mitigation), AppSec & Defensive Engineering, Deep-Dive Academic Research, Podcasts/YouTube Breakdowns, and Advanced Threat Actors.
   - Synchronized from: [Master Cybersecurity Daily Intel](https://docs.google.com/document/d/e/2PACX-1vQsdpeQlhfXV47otThYdbFlqb2GnQBrtMga4mmZxo2EvNQUhMqVlS4ATgMzKpTAxXyg3WN6eBKfSNLh/pub)

---

## ⚡ Key Features

- **Automated Daily Pipeline**: Runs every morning at **8:30 AM IST** (`03:00 UTC`) via GitHub Actions, scraping latest editions, formatting data, committing updates, and deploying to GitHub Pages.
- **Link Discipline & Canonical URLs**: Strips Google redirect tracking wrappers (`google.com/url?q=...`) to provide direct, clean canonical links to arXiv, GitHub repositories, CVE databases, and technical blogs.
- **Dual Output for Downstream AI Agents**:
  - `application/json`: Machine-readable, strictly structured JSON schema (`data/ai/latest.json`, `data/cyber/latest.json`).
  - Semantic Markdown: Clean markdown with anchors, tags, and formatted links (`data/ai/latest.md`, `data/cyber/latest.md`).
- **Interactive Web Interface**:
  - Chapter switcher (`🤖 AI Engineering` ↔ `🛡️ Cybersecurity Intel`) with URL state synchronization (`?chapter=ai` / `?chapter=cyber`).
  - Historical edition selector to browse any past date or latest release.
  - ⭐ **30-Minute Priority Sprint Card**: Highlights the single highest-leverage item of the day.
  - 🔥 **5-Minute Executive Briefing**: Quick takeaways at a glance.
  - Real-time client-side search across papers, CVEs, tools, and topics.
  - 1-Click "📋 Copy Markdown" and "{ } Copy JSON" buttons with toast notifications.
  - Dark / Light mode toggle.
  - Zero-latency initial load: embeds a static JSON snapshot so the page renders instantly without network delay.

---

## 🛠️ Repository Architecture

```
bytebreeze/
├── .github/
│   └── workflows/
│       └── daily_briefing.yml       # Scheduled pipeline at 8:30 AM IST (03:00 UTC)
├── pipeline/
│   ├── fetcher.py                  # Fetches published Google Docs with retry & header simulation
│   ├── parser_ai.py                # Parses AI Digest editions into structured JSON & Markdown
│   ├── parser_cyber.py             # Parses Cybersecurity editions into structured JSON & Markdown
│   ├── clean_urls.py               # Unquotes Google redirect tracking URLs to canonical links
│   ├── render_html.py              # Generates index.html with embedded snapshot
│   └── build.py                    # Orchestrator: fetches, parses, updates index & static files
├── data/
│   ├── index.json                  # Catalog of all available editions for both chapters
│   ├── ai/
│   │   ├── latest.json
│   │   ├── latest.md
│   │   └── editions/
│   └── cyber/
│       ├── latest.json
│       ├── latest.md
│       └── editions/
├── index.html                      # The dynamic ByteBreeze web application
├── app.js                          # Dynamic UI controller
├── style.css                       # Modern, responsive developer-tool UI
└── requirements.txt                # Python dependencies (lxml)
```

---

## 🚀 Local Development & Execution

### 1. Run Pipeline Manually
```bash
pip install -r requirements.txt
python pipeline/build.py
```

### 2. View Locally
You can open `index.html` directly in your browser, or run a local HTTP server:
```bash
python3 -m http.server 8000
```
Then visit `http://localhost:8000`.

---

## 🌐 Deploying to GitHub Pages

1. Push this repository to GitHub:
   ```bash
   git add .
   git commit -m "feat: initial bytebreeze release"
   git push -u origin main
   ```
2. In your GitHub repository:
   - Go to **Settings** → **Pages**.
   - Under **Build and deployment** > **Source**, choose **Deploy from a branch**.
   - Under **Branch**, select `main` and folder `/ (root)`.
   - Click **Save**.
3. Your site will be live at `https://amansaxna.github.io/bytebreeze/`!
4. The daily pipeline (`daily_briefing.yml`) will automatically run every morning at 8:30 AM IST, fetch the latest additions from both Google Docs, and update the site. You can also trigger it manually anytime under the **Actions** tab by selecting **Daily Intelligence Pipeline** and clicking **Run workflow**.
