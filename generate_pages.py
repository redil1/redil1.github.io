#!/usr/bin/env python3
"""Generate match preview pages using Google Gemini LLM.

Env vars:
  GEMINI_API_KEY        – your Google AI Studio key
  GEMINI_MODEL          – model name (default: gemini-pro)
  SITE_DIR              – output dir
  TARGET_CHECKOUT_URL   – your existing checkout page
"""
import os, datetime, pathlib, requests, urllib.parse, google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit("GEMINI_API_KEY not set")
genai.configure(api_key=API_KEY)
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-pro")
model = genai.GenerativeModel(MODEL_NAME)

SITE_DIR = pathlib.Path(os.getenv("SITE_DIR", "seo_site/content"))
TARGET = os.getenv("TARGET_CHECKOUT_URL", "https://www.iptv.shopping/pricing")

def write_page(home, away, start_ts):
    date_obj = datetime.datetime.fromtimestamp(start_ts)
    date_iso = date_obj.isoformat()
    date_str = date_obj.strftime('%Y-%m-%d')
    slug = f"{date_str}-{home.lower()}-vs-{away.lower()}".replace(' ', '-')
    
    prompt = (
        f"You are an elite SEO copywriter. Write a 600‑word, fully optimized preview for the football match "
        f"{home} vs {away} on {date_obj.strftime('%B %d, %Y')}. "
        "Requirements:\n"
        f"• Use the primary keyword 'watch {home} vs {away} live stream' in the H1.\n"
        "• Add synonyms and LSI terms naturally.\n"
        "• Include a micro‑schema FAQ block with 2 questions at the end.\n"
        "• Finish with a strong call‑to‑action.\n"
    )
    response = model.generate_content(prompt.format(home=home, away=away))
    content = response.text

    # Create Jekyll front matter
    front_matter = f"""---
layout: post
title: "{home} vs {away} - Match Preview"
date: {date_iso}
categories: football
---

""".format(
        home=home,
        away=away,
        date_iso=date_iso
    )

    # Create tracking URL
    track_url = f"/web/static/track.html?url={urllib.parse.quote_plus(TARGET)}&match={home}-{away}&ts={date_iso}"
    
    # Create content with call-to-action
    post_content = f"""# Watch {home} vs {away} Live Stream

{content}

<div class="text-center mt-4">
    <a href="{track_url}" class="btn btn-primary btn-lg">Watch {home} vs {away} Live in HD</a>
</div>
""".format(
        home=home,
        away=away,
        content=content,
        track_url=track_url
    )

    # Combine front matter and content
    full_content = front_matter + post_content
    
    # Create _posts directory if it doesn't exist
    (SITE_DIR / "_posts").mkdir(parents=True, exist_ok=True)
    
    # Write to file
    filename = f"{date_str}-{slug}.md"
    filepath = SITE_DIR / "_posts" / filename
    filepath.write_text(full_content, encoding='utf-8')
    
    print(f"Generated: {filename}")
    return filename

def main():
    today = datetime.datetime.utcnow()
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{today:%Y-%m-%d}"
    events = requests.get(url, timeout=10).json().get("events", [])
    for ev in events:
        write_page(ev["homeTeam"]["shortName"],
                   ev["awayTeam"]["shortName"],
                   ev["startTimestamp"])

if __name__ == "__main__":
    main()
