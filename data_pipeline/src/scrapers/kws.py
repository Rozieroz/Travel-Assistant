from playwright.sync_api import sync_playwright
from typing import List, Dict
from urllib.parse import urljoin
import time

def scrape_kws_destinations(base_url: str = "https://www.kws.go.ke") -> List[Dict]:
    destinations = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        page = context.new_page()
        
        target_url = urljoin(base_url, "/our-parks")
        print(f"Connecting to {target_url}...\n")
        page.goto(target_url, wait_until='domcontentloaded', timeout=60000)

        # 1. Improved "Load More" loop
        while True:
            # FIX: Using 'or' logic with valid Playwright locators
            # This finds either the CSS path or a link with the exact text 'Load More'
            load_more_btn = page.locator('a.button[rel="next"]').or_(page.get_by_role("link", name="Load More")).first
            
            # Check if it exists and is actually on screen
            if load_more_btn.count() > 0 and load_more_btn.is_visible():
                current_count = len(page.locator('.service-block-3').all())
                print(f"{current_count} cards found. Clicking 'Load More'...")
                
                load_more_btn.click()
                
                # Wait for the DOM to append new elements
                try:
                    page.wait_for_function(
                        f"document.querySelectorAll('.service-block-3').length > {current_count}",
                        timeout=15000
                    )
                    time.sleep(1.5) # Allow images/layout to settle
                except Exception:
                    print("Content stopped loading or reached maximum.")
                    break
            else:
                print("No more 'Load More' buttons found.")
                break

        # 2. Extraction
        final_cards = page.locator('.service-block-3').all()
        print(f"Total cards after expanding: {len(final_cards)}")
        
        for card in final_cards:
            try:
                name_elem = card.locator('h3.title span').first
                name = name_elem.inner_text().strip()
                
                link_elem = card.locator('h3.title a').first
                href = link_elem.get_attribute('href')
                
                img_elem = card.locator('.item-image img').first
                img_src = img_elem.get_attribute('src')

                destinations.append({
                    "name": name,
                    "url": urljoin(base_url, href) if href else "",
                    "image": urljoin(base_url, img_src) if img_src else "",
                    "type": "reserve" if "reserve" in name.lower() else "park"
                })
            except Exception:
                continue

        browser.close()
    return destinations

# Execution
raw_data = scrape_kws_destinations()
print(f"Extracted {len(raw_data)} destinations.")

print("Sample data:")
for item in raw_data[:8]: # Preview first 5
    print(item)

# sav as json
import json
with open("../../data/raw/kws_destinations.json", "w") as f:
    json.dump(raw_data, f, indent=2)

print("= * 50")
print("\n Data saved to data/raw/kws_destinations.json")
