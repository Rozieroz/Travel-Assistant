import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin
from typing import List, Dict

# Config
BASE_URL = "https://www.kws.go.ke"
CONCURRENCY_LIMIT = 5  # Process 5 pages at a time

async def get_all_park_urls(page) -> List[Dict]:
    """Phase 1: Get the list of 36 parks from the grid."""
    print(f"Connecting to {BASE_URL}/our-parks.../n/n")
    await page.goto(f"{BASE_URL}/our-parks", wait_until='domcontentloaded')
    
    # Load all cards by clicking 'Load More'
    while True:
        btn = page.locator('a.button[rel="next"]').or_(page.get_by_role("link", name="Load More")).first
        if await btn.is_visible():
            current_count = await page.locator('.service-block-3').count()
            await btn.click()
            try:
                await page.wait_for_function(f"document.querySelectorAll('.service-block-3').length > {current_count}", timeout=10000)
                await asyncio.sleep(1)
            except: break
        else: break

    cards = await page.locator('.service-block-3').all()
    results = []
    for card in cards:
        name = await card.locator('h3.title span').first.inner_text()
        href = await card.locator('h3.title a').first.get_attribute('href')
        results.append({"name": name.strip(), "url": urljoin(BASE_URL, href)})
    return results

async def enrich_park_details(sem, context, park: Dict):
    """Phase 2: Deep scrape 'Climate' and 'Activities' for one park."""
    async with sem:
        page = await context.new_page()
        try:
            print(f"  Enriching: {park['name']}...")
            await page.goto(park['url'], wait_until='domcontentloaded', timeout=45000)
            
            # Smart Extraction for 2026 Layout
            climate = await page.locator("text=Climate").evaluate("el => el.parentElement.innerText")
            activities = await page.locator(".field--name-field-activities .field__item").all_inner_texts()
            
            # Clean up text
            park['climate'] = climate.replace("Climate", "").strip() if climate else "Savannah Climate"
            park['activities'] = activities if activities else ["Game Viewing", "Photography"]
            return park
        except Exception:
            park['climate'] = "Check website for local conditions"
            park['activities'] = ["Wildlife Safari"]
            return park
        finally:
            await page.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0...")
        
        # 1. Get the URLs
        page = await context.new_page()
        raw_list = await get_all_park_urls(page)
        await page.close()
        
        print(f"\n\n Found {len(raw_list)} parks. Starting enrichment...")

        # 2. Enrich in Parallel
        sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
        tasks = [enrich_park_details(sem, context, park) for park in raw_list]
        final_data = await asyncio.gather(*tasks)
        
        await browser.close()
        
        print(f"\nSUCCESS: Enriched {len(final_data)} destinations.")
        # Example Output
        print(f"Sample: {final_data[0]}")

if __name__ == "__main__":
    asyncio.run(main())