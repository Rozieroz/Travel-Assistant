import requests
from bs4 import BeautifulSoup
from typing import List, Dict

def scrape_magical_kenya_list() -> List[Dict]:
    base_url = "https://magicalkenya.com/places-to-go/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status() # Check for errors
        
        soup = BeautifulSoup(response.text, 'html.parser')
        destinations = []

        # Find the containers for the destinations (CSS selectors may vary based on site updates)
        cards = soup.select('swiper-wrapper') # Replace with actual class

        for card in cards:
            data = {
                "name": card.select_one('.title-selector').text.strip(),
                "type": "destination", # You can refine this by parsing tags
                "county": card.select_one('.location-selector').text.strip(),
                "description": card.select_one('.excerpt-selector').text.strip(),
                "activities": [a.text for a in card.select('.activity-tags')]
            }
            destinations.append(data)
            
        return destinations

    except Exception as e:
        print(f"Error occurred: {e}")
        return []
    
data = scrape_magical_kenya_list()
print(data)

    
# def save_raw(data: List[Dict], filename: str):
#     with open(f"data/raw/magical_kenya_{filename}.json", "w") as f:
#         json.dump(data, f, indent=2)