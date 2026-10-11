import os
import sys
import json
import re
from datetime import datetime, timezone

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline.fetcher import fetch_url, AI_DOC_URL, CYBER_DOC_URL
from pipeline.parser_ai import parse_ai_doc
from pipeline.parser_cyber import parse_cyber_doc
from pipeline.render_html import render_index_html

def build():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(root_dir, "data")
    cache_dir = os.path.join(root_dir, ".cache")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)

    print("=== BYTEBREEZE PIPELINE STARTING ===")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")

    ai_fallback = os.path.join(cache_dir, "ai_doc.html")
    cyber_fallback = os.path.join(cache_dir, "cyber_doc.html")

    # If cache doesn't exist, check parent brain step files
    brain_ai = "/Users/amansaxena/.gemini/antigravity/brain/8ef3a458-dd41-4b2d-8ece-9cbb011fe4a5/.system_generated/steps/2/content.md"
    brain_cyber = "/Users/amansaxena/.gemini/antigravity/brain/8ef3a458-dd41-4b2d-8ece-9cbb011fe4a5/.system_generated/steps/3/content.md"
    if not os.path.exists(ai_fallback) and os.path.exists(brain_ai):
        with open(brain_ai, "r") as f:
            open(ai_fallback, "w").write(f.read())
    if not os.path.exists(cyber_fallback) and os.path.exists(brain_cyber):
        with open(brain_cyber, "r") as f:
            open(cyber_fallback, "w").write(f.read())

    # 1. Fetch AI Doc
    print("Fetching AI Doc...")
    ai_html = fetch_url(AI_DOC_URL, fallback_path=ai_fallback)
    ai_editions = parse_ai_doc(ai_html)
    print(f"Parsed {len(ai_editions)} AI Digest edition(s).")

    # 2. Fetch Cyber Doc
    print("Fetching Cybersecurity Doc...")
    cyber_html = fetch_url(CYBER_DOC_URL, fallback_path=cyber_fallback)
    cyber_editions = parse_cyber_doc(cyber_html)
    print(f"Parsed {len(cyber_editions)} Cybersecurity edition(s).")

    # Setup directories
    ai_dir = os.path.join(data_dir, "ai")
    ai_ed_dir = os.path.join(ai_dir, "editions")
    cyber_dir = os.path.join(data_dir, "cyber")
    cyber_ed_dir = os.path.join(cyber_dir, "editions")
    os.makedirs(ai_ed_dir, exist_ok=True)
    os.makedirs(cyber_ed_dir, exist_ok=True)

    # Save AI editions
    ai_index = []
    for idx, ed in enumerate(ai_editions):
        slug = re.sub(r'[^a-zA-Z0-9-]', '-', ed["metadata"]["date"].lower()).strip('-') or f"edition-{idx+1}"
        file_path = os.path.join(ai_ed_dir, f"{slug}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(ed, f, indent=2, ensure_ascii=False)
        ai_index.append({
            "id": slug,
            "title": ed["metadata"]["edition_title"],
            "date": ed["metadata"]["date"],
            "topics_count": len(ed.get("topics", [])),
            "file": f"data/ai/editions/{slug}.json"
        })

    # The latest entry for AI (first or last edition)
    latest_ai = ai_editions[0] if ai_editions else None
    if latest_ai:
        with open(os.path.join(ai_dir, "latest.json"), "w", encoding="utf-8") as f:
            json.dump(latest_ai, f, indent=2, ensure_ascii=False)
        with open(os.path.join(ai_dir, "latest.md"), "w", encoding="utf-8") as f:
            f.write(latest_ai.get("markdown", ""))

    # Save Cyber editions (cyber editions are in chronological order, so latest is last)
    cyber_index = []
    for idx, ed in enumerate(cyber_editions):
        slug = ed["metadata"]["date"] or f"edition-{idx+1}"
        file_path = os.path.join(cyber_ed_dir, f"{slug}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(ed, f, indent=2, ensure_ascii=False)
        cyber_index.append({
            "id": slug,
            "title": ed["metadata"]["edition_title"],
            "date": ed["metadata"]["date"],
            "topics_count": len(ed.get("topics", [])),
            "file": f"data/cyber/editions/{slug}.json"
        })

    latest_cyber = cyber_editions[-1] if cyber_editions else None
    if latest_cyber:
        with open(os.path.join(cyber_dir, "latest.json"), "w", encoding="utf-8") as f:
            json.dump(latest_cyber, f, indent=2, ensure_ascii=False)
        with open(os.path.join(cyber_dir, "latest.md"), "w", encoding="utf-8") as f:
            f.write(latest_cyber.get("markdown", ""))

    # Index catalog
    index_catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "chapters": {
            "ai": {
                "name": "AI Engineering Digest",
                "tagline": "High-signal daily intelligence for software engineers leveling up in AI/ML systems",
                "icon": "🤖",
                "latest_date": latest_ai["metadata"]["date"] if latest_ai else None,
                "latest_file": "data/ai/latest.json",
                "editions": ai_index
            },
            "cyber": {
                "name": "Cybersecurity & Threat Intelligence",
                "tagline": "Daily zero-days, runtime reachability, kernel exploits & threat actor breakdowns",
                "icon": "🛡️",
                "latest_date": latest_cyber["metadata"]["date"] if latest_cyber else None,
                "latest_file": "data/cyber/latest.json",
                "editions": list(reversed(cyber_index))  # newest first in list
            }
        }
    }

    with open(os.path.join(data_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index_catalog, f, indent=2, ensure_ascii=False)

    # Render static HTML with embedded initial state
    render_index_html()

    print("=== BYTEBREEZE PIPELINE COMPLETE ===")
    print(f"Data files written to: {data_dir}")

if __name__ == "__main__":
    build()
