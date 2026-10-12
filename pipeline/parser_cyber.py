import re
from typing import Dict, Any, List
import lxml.html
from .clean_urls import clean_google_url

def parse_cyber_doc(html_content: str) -> List[Dict[str, Any]]:
    """
    Parses Google Doc published HTML for Master Cybersecurity Daily Intel.
    Returns a list of structured editions, newest last or by date.
    """
    doc = lxml.html.fromstring(html_content)
    content_divs = doc.xpath('//div[contains(@class, "doc-content")]')
    if not content_divs:
        # Fallback to body
        content_div = doc.xpath('//body')[0]
    else:
        content_div = content_divs[0]

    nodes = list(content_div)
    editions = []
    curr_edition = None

    for node in nodes:
        txt = node.text_content().strip()
        if "Daily Cybersecurity" in txt and ("202" in txt or "—" in txt):
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', txt)
            date_str = date_match.group(1) if date_match else "unknown"
            curr_edition = {
                "chapter": "cybersecurity",
                "date": date_str,
                "raw_title": txt,
                "nodes": []
            }
            editions.append(curr_edition)
        elif curr_edition is not None:
            curr_edition["nodes"].append(node)

    parsed_editions = []
    for ed in editions:
        parsed_editions.append(_build_cyber_edition(ed["raw_title"], ed["date"], ed["nodes"]))

    return parsed_editions

def _build_cyber_edition(raw_title: str, date_str: str, nodes: list) -> Dict[str, Any]:
    sections = []
    curr_sec = None
    curr_sub = None

    for n in nodes:
        txt = n.text_content().strip()
        if not txt:
            continue

        if n.tag == 'h1':
            topic_id = _slugify(txt)
            icon = _extract_icon(txt, default="shield-check")
            curr_sec = {
                "topic_id": topic_id,
                "topic_title": txt,
                "icon": icon,
                "subtopics": []
            }
            sections.append(curr_sec)
            curr_sub = None

        elif n.tag == 'h2':
            # Subtopic title
            a_tags = n.xpath('.//a')
            url = clean_google_url(a_tags[0].get('href')) if a_tags else ""
            curr_sub = {
                "title": txt,
                "url": url,
                "details": {},
                "summary": "",
                "primary_sources": [],
                "bullets": []
            }
            if curr_sec:
                curr_sec["subtopics"].append(curr_sub)

        elif n.tag in ['ul', 'ol']:
            if curr_sub:
                lis = n.xpath('.//li')
                for li in lis:
                    li_text = li.text_content().strip()
                    links = []
                    for a in li.xpath('.//a'):
                        clean_href = clean_google_url(a.get('href'))
                        link_text = a.text_content().strip()
                        if clean_href:
                            links.append({"name": link_text or "Source", "url": clean_href})

                    # Check for Key: Value format
                    parts = li_text.split(":", 1)
                    if len(parts) == 2 and len(parts[0]) <= 50 and not parts[0].startswith("http"):
                        key = parts[0].strip()
                        val = parts[1].strip()
                        curr_sub["details"][key] = {
                            "text": val,
                            "links": links
                        }
                        if key.lower() in ["primary sources", "primary source"]:
                            curr_sub["primary_sources"].extend(links)
                        if not curr_sub["summary"] and key.lower() in ["impact vector", "engineering takeaways", "the core threat model", "strategic impact"]:
                            curr_sub["summary"] = val
                        if not curr_sub.get("url") and links:
                            curr_sub["url"] = links[0]["url"]
                    else:
                        curr_sub["bullets"].append({
                            "text": li_text,
                            "links": links
                        })

    # Build quick takeaways from Critical Vulnerabilities & Threat Actors
    quick_takeaways = []
    for sec in sections:
        for sub in sec["subtopics"]:
            if "Impact Vector" in sub["details"]:
                quick_takeaways.append(f"{sub['title']}: {sub['details']['Impact Vector']['text'][:160]}...")
            elif "Engineering Takeaways" in sub["details"]:
                quick_takeaways.append(f"{sub['title']}: {sub['details']['Engineering Takeaways']['text'][:160]}...")

    # Pick top 30-min priority item
    high_leverage = {
        "title": sections[0]["subtopics"][0]["title"] if sections and sections[0]["subtopics"] else "Critical Threat Vector",
        "url": sections[0]["subtopics"][0]["url"] if sections and sections[0]["subtopics"] else "",
        "rationale": "High-severity threat vector with in-the-wild exploitation requiring immediate mitigation review."
    }

    metadata = {
        "date": date_str,
        "edition_title": raw_title,
        "target_audience": "Security Engineers, AppSec Architects & Threat Intel Teams",
        "quick_takeaway_5_min": quick_takeaways[:5],
        "high_leverage_30_min_pick": high_leverage
    }

    markdown_str = _render_cyber_markdown(metadata, sections)

    return {
        "chapter": "cybersecurity",
        "metadata": metadata,
        "topics": sections,
        "markdown": markdown_str
    }

def _slugify(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip().lower()
    return re.sub(r'[\s_]+', '-', cleaned) or "section"

def _extract_icon(text: str, default: str) -> str:
    if "🔴" in text or "vulnerabilit" in text.lower(): return "shield-exclamation"
    if "🏗️" in text or "appsec" in text.lower(): return "cube-transparent"
    if "🔬" in text or "research" in text.lower(): return "beaker"
    if "🎙️" in text or "podcast" in text.lower(): return "microphone"
    if "🌐" in text or "threat" in text.lower(): return "globe-alt"
    return default

def _render_cyber_markdown(metadata: dict, topics: list) -> str:
    lines = [
        f"# {metadata['edition_title']}",
        f"**Date**: {metadata['date']} | **Target Audience**: {metadata['target_audience']}",
        "",
        "## 🔥 Executive Briefing & Key Indicators",
    ]
    for q in metadata.get("quick_takeaway_5_min", []):
        lines.append(f"- {q}")

    hl = metadata.get("high_leverage_30_min_pick", {})
    if hl.get("title"):
        lines.append("")
        lines.append(f"## ⭐ 30-Minute Priority Sprint: [{hl['title']}]({hl['url']})")
        lines.append(f"> {hl.get('rationale', '')}")

    lines.append("")

    for t in topics:
        lines.append(f"## {t['topic_title']}")
        for sub in t.get("subtopics", []):
            if sub.get("url"):
                lines.append(f"### [{sub['title']}]({sub['url']})")
            else:
                lines.append(f"### {sub['title']}")

            for k, v in sub.get("details", {}).items():
                links_md = ""
                if v.get("links"):
                    links_md = " (" + ", ".join([f"[{link['name']}]({link['url']})" for link in v["links"]]) + ")"
                lines.append(f"- **{k}**: {v.get('text', '')}{links_md}")

            for b in sub.get("bullets", []):
                links_md = ""
                if b.get("links"):
                    links_md = " (" + ", ".join([f"[{link['name']}]({link['url']})" for link in b["links"]]) + ")"
                lines.append(f"- {b['text']}{links_md}")
            lines.append("")

    return "\n".join(lines)
