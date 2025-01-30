import json
import os
import re
import string
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

# File configuration
INPUT_FILE = "products.jsonl"
PROCESSED_FILE = "processed_products.jsonl"
INDEX_FOLDER = "index"  # Directory for storing indexes

# Common English stopwords
STOPWORDS = set(["the", "a", "an", "and", "or", "of", "to", "in", "on", "with", "for", "by", "at", "from", 
                 "is", "it", "this", "that", "as", "are", "was", "were", "be", "been", "has", "have", "had"])


def extract_product_info_from_url(url):
    """Extracts product ID and variant from the URL."""
    try:
        match = re.search(r"/product/(\d+)", url)
        product_id = match.group(1) if match else None

        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        variant_id = query_params.get("variant", [None])[0]

        return {"product_id": product_id, "variant": variant_id}
    except Exception as e:
        print(f"Error parsing URL: {url}. Error: {e}")
        return {"product_id": None, "variant": None}


def load_data(filename):
    """Loads data from a JSONL file."""
    if not os.path.exists(filename):
        print(f"Error: File {filename} does not exist.")
        return []
    
    data = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            try:
                data.append(json.loads(line.strip()))
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
    return data


def save_data(data, filename):
    """Saves data to a JSONL file."""
    with open(filename, "w", encoding="utf-8") as file:
        for doc in data:
            file.write(json.dumps(doc, ensure_ascii=False) + "\n")


def tokenize(text):
    """Tokenizes text by removing punctuation and stopwords."""
    if not text:
        return []
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return [word for word in text.split() if word not in STOPWORDS]


def build_inverted_index_with_positions(field, data):
    """Builds an inverted index with positions for a given field."""
    index = defaultdict(lambda: defaultdict(list))
    for doc in data:
        tokens = tokenize(doc.get(field, ""))
        for pos, token in enumerate(tokens):
            index[token][doc['url']].append(pos)
    return index


def build_reviews_index(data):
    """Creates an index for reviews including total count, average rating, and last rating."""
    index = {}
    for doc in data:
        reviews = doc.get("product_reviews", [])
        if reviews:
            total_reviews = len(reviews)
            avg_rating = sum(r.get("rating", 0) for r in reviews) / total_reviews
            last_rating = reviews[-1].get("rating", None)
            index[doc['url']] = {"total_reviews": total_reviews, "average_rating": avg_rating, "last_rating": last_rating}
    return index


def build_feature_index(data, feature_name, feature_key):
    """Builds an inverted index for a specific feature (e.g., brand, origin)."""
    index = defaultdict(set)
    for doc in data:
        feature_value = doc.get("product_features", {}).get(feature_key, "")
        for token in tokenize(str(feature_value)):
            index[token].add(doc['url'])
    return {token: list(urls) for token, urls in index.items()}


def save_index(index, filename):
    """Saves an index to a JSON file."""
    os.makedirs(INDEX_FOLDER, exist_ok=True)
    with open(os.path.join(INDEX_FOLDER, filename), "w", encoding="utf-8") as file:
        json.dump(index, file, indent=4, ensure_ascii=False)


def run_pipeline():
    """Executes the full pipeline."""
    data = load_data(INPUT_FILE)
    if not data:
        print("No data loaded, stopping pipeline.")
        return
    
    # Extract product information from URL
    processed_data = [doc | extract_product_info_from_url(doc.get("url", "")) for doc in data]
    save_data(processed_data, PROCESSED_FILE)
    print("Processed data saved!")
    
    # Build indexes
    title_index = build_inverted_index_with_positions("title", processed_data)
    description_index = build_inverted_index_with_positions("description", processed_data)
    reviews_index = build_reviews_index(processed_data)
    brand_index = build_feature_index(processed_data, "brand", "brand")
    origin_index = build_feature_index(processed_data, "made_in", "made in")
    
    # Save indexes
    save_index(title_index, "index_title.json")
    save_index(description_index, "index_description.json")
    save_index(reviews_index, "index_reviews.json")
    save_index(brand_index, "index_brand.json")
    save_index(origin_index, "index_made_in.json")
    
    print("All indexes generated and saved!")


if __name__ == "__main__":
    run_pipeline()
