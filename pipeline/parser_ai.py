import re
from typing import Dict, Any, List
import lxml.html
from .clean_urls import clean_google_url

def parse_ai_doc(html_content: str) -> List[Dict[str, Any]]:
    """
    Parses Google Doc published HTML for Daily AI Engineering Learning Digest.
    Returns a list of structured editions.
    """
    doc = lxml.html.fromstring(html_content)
    content_divs = doc.xpath('//div[contains(@class, "doc-content")]')
    content_div = content_divs[0] if content_divs else doc.xpath('//body')[0]

    nodes = list(content_div)
    editions = []
    curr_edition = None

    for node in nodes:
        txt = node.text_content().strip()
        # Look for edition boundary header
        if "Daily AI Engineering" in txt and node.tag in ['h1', 'p'] and ("October" in txt or "202" in txt or "—" in txt):
            date_match = re.search(r'([A-Za-z]+ \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2})', txt)
            date_str = date_match.group(1) if date_match else "Latest"
            curr_edition = {
                "chapter": "ai",
                "raw_title": txt,
                "date": date_str,
                "nodes": []
            }
            editions.append(curr_edition)
        elif curr_edition is not None:
            curr_edition["nodes"].append(node)

    parsed = []
    for idx, ed in enumerate(editions):
        parsed.append(_build_ai_edition(ed["raw_title"], ed["date"], ed["nodes"], edition_index=idx+1))

    return parsed

def _build_ai_edition(raw_title: str, date_str: str, nodes: list, edition_index: int = 1) -> Dict[str, Any]:
    quick_takeaways = []
    high_leverage = {}
    topics = []
    curr_topic = None
    curr_sub = None

    for n in nodes:
        txt = n.text_content().strip()
        if not txt:
            continue

        # 5-minute summary list
        if "5-minute summary" in txt.lower() or "5-min" in txt.lower():
            continue

        # If 30-min priority sprint pick
        if "if i only have 30 minutes" in txt.lower() or "30-minute priority" in txt.lower():
            a_tags = n.xpath('.//a')
            url = clean_google_url(a_tags[0].get('href')) if a_tags else ""
            high_leverage = {
                "title": txt.split(":", 1)[0].replace("⭐", "").strip(),
                "url": url,
                "rationale": txt.split(":", 1)[1].strip() if ":" in txt else txt
            }
            continue

        # Check for Section header (h2)
        if n.tag == 'h2':
            topic_id = _map_ai_topic_id(txt)
            icon = _map_ai_icon(topic_id)
            curr_topic = {
                "topic_id": topic_id,
                "topic_title": txt,
                "icon": icon,
                "subtopics": []
            }
            topics.append(curr_topic)
            curr_sub = None
            continue

        # Check for list items
        if n.tag in ['ol', 'ul']:
            lis = n.xpath('.//li')
            # If we don't have a topic yet, these might be 5-minute takeaways
            if not curr_topic:
                for li in lis:
                    quick_takeaways.append(li.text_content().strip())
                continue

            # Within topics:
            # If the ul contains a bold title or link, it's a subtopic header
            # Otherwise it's subtopic details
            for li in lis:
                li_text = li.text_content().strip()
                a_tags = li.xpath('.//a')
                links = [{"name": a.text_content().strip() or "Link", "url": clean_google_url(a.get('href'))} for a in a_tags if clean_google_url(a.get('href'))]

                # Check if this is a subtopic title vs subtopic field
                # Typically subtopics start with paper/tool title, or have Authors/Summary/What it does
                has_field_prefix = any(li_text.lower().startswith(p) for p in [
                    "authors", "release date", "summary:", "why it matters:", "practical takeaway:", 
                    "key concept", "what it does:", "why it matters", "experimentation idea:", "channel:", 
                    "signal:", "platform:", "simple explanation", "mental model", "mechanics", "architecture", 
                    "production", "priority focus", "why:"
                ])

                if not has_field_prefix and (len(a_tags) > 0 or len(li_text) < 140) and curr_topic["topic_id"] in ["research-papers", "tools-and-repositories", "video-breakdowns", "technical-discussions"]:
                    # Create new subtopic
                    sub_url = links[0]["url"] if links else ""
                    curr_sub = {
                        "title": li_text,
                        "primary_url": sub_url,
                        "summary": "",
                        "details": {},
                        "tags": []
                    }
                    curr_topic["subtopics"].append(curr_sub)
                else:
                    # It's detail information
                    if not curr_sub:
                        # Fallback create subtopic
                        curr_sub = {
                            "title": li_text[:80] + ("..." if len(li_text) > 80 else ""),
                            "primary_url": links[0]["url"] if links else "",
                            "summary": "",
                            "details": {},
                            "tags": []
                        }
                        curr_topic["subtopics"].append(curr_sub)

                    # Store key-value or raw bullet
                    parts = li_text.split(":", 1)
                    if len(parts) == 2 and len(parts[0]) <= 40:
                        key = parts[0].strip()
                        val = parts[1].strip()
                        curr_sub["details"][key] = {
                            "text": val,
                            "links": links
                        }
                        if key.lower() == "summary":
                            curr_sub["summary"] = val
                    else:
                        if "bullets" not in curr_sub["details"]:
                            curr_sub["details"]["bullets"] = []
                        curr_sub["details"]["bullets"].append({
                            "text": li_text,
                            "links": links
                        })

    if not high_leverage and topics and topics[0]["subtopics"]:
        high_leverage = {
            "title": topics[0]["subtopics"][0]["title"],
            "url": topics[0]["subtopics"][0].get("primary_url", ""),
            "rationale": "High-leverage technical advancement for AI engineers."
        }

    metadata = {
        "date": date_str,
        "edition_title": raw_title,
        "edition_number": edition_index,
        "target_audience": "Software Engineers Transitioning to AI/ML Systems",
        "quick_takeaway_5_min": quick_takeaways[:5],
        "high_leverage_30_min_pick": high_leverage
    }

    markdown_str = _render_ai_markdown(metadata, topics)

    return {
        "chapter": "ai",
        "metadata": metadata,
        "topics": topics,
        "markdown": markdown_str
    }

def _map_ai_topic_id(text: str) -> str:
    t = text.lower()
    if "2." in t or "practitioner" in t or "educator" in t or "follow" in t or "voices" in t: return "practitioners"
    if "1." in t or "paper" in t or "breakthrough" in t or "research" in t: return "research-papers"
    if "3." in t or "discussion" in t or "debate" in t: return "technical-discussions"
    if "4." in t or "video" in t or "youtube" in t: return "video-breakdowns"
    if "5." in t or "tool" in t or "repositor" in t or "open-source" in t or "framework" in t: return "tools-and-repositories"
    if "6." in t or "concept of the day" in t: return "concept-of-the-day"
    if "7." in t or "action plan" in t or "learn today" in t or "60" in t: return "actionable-learning-plan"
    if "8." in t or "career" in t or "relevance" in t or "domain" in t: return "career-relevance"
    return re.sub(r'[^a-zA-Z0-9]+', '-', t).strip('-')

def _map_ai_icon(topic_id: str) -> str:
    mapping = {
        "research-papers": "academic-cap",
        "practitioners": "user-group",
        "technical-discussions": "chat-bubble-left-right",
        "video-breakdowns": "video-camera",
        "tools-and-repositories": "code-bracket",
        "concept-of-the-day": "light-bulb",
        "actionable-learning-plan": "clock",
        "career-relevance": "briefcase"
    }
    return mapping.get(topic_id, "document-text")

def _render_ai_markdown(metadata: dict, topics: list) -> str:
    lines = [
        f"# {metadata['edition_title']}",
        f"**Date**: {metadata['date']} | **Audience**: {metadata['target_audience']}",
        "",
        "## 🔥 Today's 5-Minute Summary"
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
            url_part = f"[{sub['title']}]({sub['primary_url']})" if sub.get("primary_url") else sub["title"]
            lines.append(f"### {url_part}")
            for k, v in sub.get("details", {}).items():
                if k == "bullets":
                    continue
                links_md = ""
                if v.get("links"):
                    links_md = " (" + ", ".join([f"[{link['name']}]({link['url']})" for link in v["links"]]) + ")"
                lines.append(f"- **{k}**: {v.get('text', '')}{links_md}")

            for b in sub.get("details", {}).get("bullets", []):
                links_md = ""
                if b.get("links"):
                    links_md = " (" + ", ".join([f"[{link['name']}]({link['url']})" for link in b["links"]]) + ")"
                lines.append(f"- {b['text']}{links_md}")
            lines.append("")

    return "\n".join(lines)
