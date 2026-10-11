import urllib.request
import os

AI_DOC_URL = "https://docs.google.com/document/d/e/2PACX-1vQhw17LLem50H4hn6f_TJRCzFo6r3ec_KgBFFYZcgUMYnjLS8tQqiCem42xrLGj2w0BNxE5o5wkv5xq/pub"
CYBER_DOC_URL = "https://docs.google.com/document/d/e/2PACX-1vQsdpeQlhfXV47otThYdbFlqb2GnQBrtMga4mmZxo2EvNQUhMqVlS4ATgMzKpTAxXyg3WN6eBKfSNLh/pub"

def fetch_url(url: str, fallback_path: str = None) -> str:
    """Fetch published Google Doc HTML with realistic User-Agent and offline fallback."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read().decode("utf-8")
            if fallback_path:
                os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
                with open(fallback_path, "w", encoding="utf-8") as f:
                    f.write(content)
            return content
    except Exception as e:
        print(f"Warning: Failed to fetch {url}: {e}")
        if fallback_path and os.path.exists(fallback_path):
            print(f"Using fallback file: {fallback_path}")
            with open(fallback_path, "r", encoding="utf-8") as f:
                return f.read()
        raise e
