# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    crawler.py                                         :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ccottet <ccottet@student.42.fr>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/01/30 16:33:46 by ccottet           #+#    #+#              #
#    Updated: 2025/01/30 16:33:48 by ccottet          ###   ########.fr        #
#                                                                              #
# **************************************************************************** #


import time
import json
from utils import get_urls, can_fetch, extract_page_data

def fetch_page(url, crawled_urls):
    """
    Télécharge et extrait les données d'une page web si elle est autorisée par robots.txt.

    Args:
        url (str): L'URL de la page à récupérer.
        crawled_urls (set): Ensemble des URLs déjà explorées.

    Returns:
        dict or None: Les données extraites de la page sous forme de dictionnaire,
                      ou None si la page ne peut pas être récupérée.
    """

    if url and can_fetch(url):
        crawled_urls.add(url)
        page_data = extract_page_data(url)

        # Pause de 5 secondes pour éviter d'être détecté comme un bot (limite le risque de bannissement)
        time.sleep(5)
        return page_data

    # Retourne None si l'URL ne peut pas être explorée
    return None


def crawl(start_url, max_urls=50):
    crawled_urls = set()
    urls_to_crawl = set(get_urls(start_url))
    priority_urls = set()  # Stocke les URLs contenant "product"
    results = []

    if not urls_to_crawl:
        urls_to_crawl = {start_url}

    # Séparation des URLs en prioritaires et non prioritaires
    for url in list(urls_to_crawl):
        if "product" in url:
            priority_urls.add(url)
            urls_to_crawl.remove(url)

    while (priority_urls or urls_to_crawl) and len(crawled_urls) < max_urls:
        # Prioriser les URLs contenant "product"
        if priority_urls:
            url = priority_urls.pop()
        else:
            url = urls_to_crawl.pop()

        page_data = fetch_page(url, crawled_urls)
        if page_data:
            results.append(page_data)
            links = page_data.get("links", [])


            for link in links:
                if link not in crawled_urls and len(crawled_urls) < max_urls:
                    if "product" in link:
                        priority_urls.add(link)  # Ajouter en priorité
                    else:
                        urls_to_crawl.add(link)

    # Sauvegarde des résultats
    print("Écriture des données dans un fichier JSON...")
    with open('crawled_webpages.json', 'w', encoding='utf-8') as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    return results
