import json
import time
import urllib.request
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests
import xml.etree.ElementTree as ET

def can_fetch(url, user_agent='*'):
    rp = RobotFileParser()
    rp.set_url(urllib.request.urljoin(url, '/robots.txt'))
    rp.read()
    return rp.can_fetch(user_agent, url)

def get_urls(start_url):
    """
    Extract all valid URLs from the given web page.

    Args:
        start_url (str): The URL of the page to extract links from.

    Returns:
        list: A list of valid and absolute URLs found on the page.
    """
    try:
        response = requests.get(start_url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        soup = BeautifulSoup(response.text, 'html.parser')

        base_url = start_url # Filter to stay within this domain
        links = set()

        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            absolute_url = urljoin(start_url, href)

            # Ensure the link belongs to the same domain and is not external
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                links.add(absolute_url)

        return list(links)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {start_url}: {e}")
        return []



def extract_page_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraire le titre
        title = soup.title.string.strip() if soup.title else "Pas de titre"

        # Extraire la description du produit (si disponible)
        product_description_tag = soup.find('p', class_="product-description")
        product_description = product_description_tag.get_text().strip() if product_description_tag else ""

        # Extraire le premier paragraphe (si pas de description produit)
        first_paragraph_tag = soup.find('p')
        first_paragraph = first_paragraph_tag.get_text().strip() if first_paragraph_tag else ""

        # Extraction des liens
        links = set()
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            absolute_url = urljoin(url, href)

            # S'assurer que le lien appartient au même domaine
            if urlparse(absolute_url).netloc == urlparse(url).netloc:
                links.add(absolute_url)

        return {
            "title": title,
            "url": url,
            "first_paragraph": product_description if product_description else first_paragraph,
            "links": list(links)  # Convertir en liste
        }

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'extraction des données de {url}: {e}")
        return None
