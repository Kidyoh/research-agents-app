from typing import List, Dict
import requests
from bs4 import BeautifulSoup

def perform_web_search(query: str) -> List[Dict[str, str]]:
    search_url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    response = requests.get(search_url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    
    for g in soup.find_all('div', class_='g'):
        title = g.find('h3').text if g.find('h3') else ''
        link = g.find('a')['href'] if g.find('a') else ''
        snippet = g.find('span', class_='aCOpRe').text if g.find('span', class_='aCOpRe') else ''
        
        results.append({
            'title': title,
            'link': link,
            'snippet': snippet
        })
    
    return results

def save_facts(facts: List[Dict[str, str]], source: str) -> None:
    # This function would implement logic to save facts with source attribution
    pass