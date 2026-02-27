from playwright.sync_api import sync_playwright
from typing import List, Dict
import time

def scrape_magical_kenya_list() -> List[Dict]:
    destinations = []
    
    with sync_playwright() as p:
        # 1. Setup with a realistic User-Agent to avoid blocks
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("Navigating to Magical Kenya... \n")
        page.goto("https://magicalkenya.com/places-to-go/", wait_until="domcontentloaded", timeout=60000)

        # 2. Trigger Lazy Loading
        # We scroll in increments to ensure the browser registers the cards
        for _ in range(3):
            page.mouse.wheel(0, 1500)
            time.sleep(2)

        # 3. Target the specific Link Pattern
        # This targets any link that looks like a city/destination page
        links = page.locator('a[href*="/city/"], a[href*="/destination/"]').all()
        
        print(f"🔍 Found {len(links)} potential destination links. Extracting data...")

        for link in links:
            try:
                url = link.get_attribute("href")
                raw_text = link.inner_text().strip()
                
                if not raw_text:
                    continue

                # Split the text by newline
                # Index 0 is usually the Name, the rest is the description
                parts = raw_text.split('\n')
                name = parts[0].strip().title() # "Eldoret" instead of "ELDORET"
                description = " ".join(parts[1:]).strip() if len(parts) > 1 else ""

                if name and url and name not in [d['name'] for d in destinations]:
                    destinations.append({
                        "name": name,
                        "description": description,
                        "url": url,
                        "type": "City" if "/city/" in url else "Destination"
                    })
            except Exception:
                continue

        browser.close()
        
    print(f"✅ Successfully extracted {len(destinations)} destinations.")
    return destinations

# Run it
data = scrape_magical_kenya_list()
for item in data[:5]: # Preview first 5
    print(item)