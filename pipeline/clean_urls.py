import urllib.parse

def clean_google_url(url: str) -> str:
    """Strip Google Docs redirect tracking wrappers to yield canonical URLs."""
    if not url:
        return ""
    url = url.strip()
    if "google.com/url?q=" in url:
        try:
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            if "q" in qs and qs["q"]:
                return qs["q"][0]
        except Exception:
            pass
    return url
