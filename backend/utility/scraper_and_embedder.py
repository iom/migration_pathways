# scraper_and_embedder.py
import os
import requests
import hashlib
from bs4 import BeautifulSoup
from typing import List, Dict
from dotenv import load_dotenv
import json 
import datetime

load_dotenv()

# # (Wakawell pages)
# wakawell_urls = [
#     "https://www.wakawell.info/en",
#     "https://www.wakawell.info/en/learn",
#     "https://www.wakawell.info/en/about-us",
#     "https://www.wakawell.info/en/advocacy#no-back",
#     "https://www.wakawell.info/en/visa-wizard",
#     "https://www.wakawell.info/en/departure-senegal",
#     "https://www.wakawell.info/en/destination-guinea",
#     "https://www.wakawell.info/en/destination-mali",
#     "https://www.wakawell.info/en/destination-niger",
#     "https://www.wakawell.info/en/destination-mauritania",
#     "https://www.wakawell.info/en/destination-nigeria"
# ]

def load_urls_from_config() -> List[str]:
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "urls.json"))
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            urls = json.load(f)
            return urls if isinstance(urls, list) else []
    except Exception as e:
        print(f"[ERROR] Failed to load URLs from config: {e}")
        return []


def get_page_content(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        print(f"[ERROR] Failed to fetch {url} - Status code: {response.status_code}")
        return ""


def extract_main_content(soup: BeautifulSoup) -> str:
    for elem in soup.find_all(['nav', 'header', 'footer', 'script', 'style']):
        elem.decompose()

    main_content = soup.find(['main', 'article', 'section'])
    if main_content:
        return ' '.join(main_content.get_text(separator=' ', strip=True).split())

    return ' '.join(soup.get_text(separator=' ', strip=True).split())

def extract_content_from_url(url: str) -> Dict:
    html = get_page_content(url)
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string.strip() if soup.title else ""
    canonical_url = soup.find('link', {'rel': 'canonical'})
    canonical_url = canonical_url['href'] if canonical_url else url

    main_content = extract_main_content(soup)
    content_hash = hashlib.md5(main_content.encode('utf-8')).hexdigest()

    return {
        "url": canonical_url,
        "title": title,
        "hash": content_hash,
        "text": main_content
    }

def scrape_wakawell_pages() -> List[Dict]:
    urls_to_scrape = load_urls_from_config()
    print(f"Scraping {len(urls_to_scrape)} pages from config/urls.json...\n")

    content_list = []
    seen_hashes = set()

    for url in urls_to_scrape:
        content = extract_content_from_url(url)
        if content and content["hash"] not in seen_hashes:
            seen_hashes.add(content["hash"])
            content_list.append(content)
        else:
            print(f"⚠️ Skipped duplicate or empty: {url}")

    print(f"\nSuccessfully scraped {len(content_list)} unique pages.")
    return content_list

# Test if running directly
if __name__ == "__main__":
    results = scrape_wakawell_pages()
    for item in results:
        print(f"\n Page: {item['title']}\nURL: {item['url']}\n")
    
    # Save full scrape for QA
    # with open("scraped_data_full.json", "w", encoding="utf-8") as f:
    #     json.dump(results, f, indent=2, ensure_ascii=False)
    # print("📝 Full scraped data saved to scraped_data_full.json")
    
    # Generate timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    filename = f"scraped_data_{timestamp}.json"

    # Save versioned file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f" Full scraped data saved to {filename}")

    # Also save/update latest copy for frontend/API
    with open("scraped_data_full.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(" Updated scraped_data_full.json with latest content")