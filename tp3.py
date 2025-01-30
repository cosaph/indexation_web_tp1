# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    tp3.py                                             :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ccottet <ccottet@student.42.fr>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/01/30 16:32:28 by ccottet           #+#    #+#              #
#    Updated: 2025/01/30 16:33:28 by ccottet          ###   ########.fr        #
#                                                                              #
# **************************************************************************** #


import json
import math
import re
import os
from datetime import datetime
from typing import Dict, List, Set, Tuple

# STOPWORDS
STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", 
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", 
    "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", 
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that", 
    "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", 
    "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", 
    "at", "by", "for", "with", "about", "against", "between", "into", "through", 
    "during", "before", "after", "above", "below", "to", "from", "up", "down", 
    "in", "out", "on", "off", "over", "under", "again", "further", "then", 
    "once", "here", "there", "when", "where", "why", "how", "all", "any", 
    "both", "each", "few", "more", "most", "other", "some", "such", "no", 
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", 
    "t", "can", "will", "just", "don", "should", "now"
}

class SearchEngine:
    def __init__(self, index_path: str = "fichier_prof/"):
        """Initialize the search engine by loading all required indexes."""
        # Load all indexes from the provided path
        with open(f"{index_path}brand_index.json", "r") as f:
            self.brand_index = json.load(f)
        with open(f"{index_path}description_index.json", "r") as f:
            self.description_index = json.load(f)
        with open(f"{index_path}domain_index.json", "r") as f:
            self.domain_index = json.load(f)
        with open(f"{index_path}origin_index.json", "r") as f:
            self.origin_index = json.load(f)
        with open(f"{index_path}origin_synonyms.json", "r") as f:
            self.origin_synonyms = json.load(f)
        with open(f"{index_path}reviews_index.json", "r") as f:
            self.reviews_index = json.load(f)
        with open(f"{index_path}title_index.json", "r") as f:
            self.title_index = json.load(f)

        # Load product data
        self.products = {}
        with open(f"{index_path}rearranged_products.jsonl", "r") as f:
            for line in f:
                product = json.loads(line)
                self.products[product["url"]] = product

        # Create results directory if it doesn't exist
        base_path = os.path.dirname(index_path.rstrip('/'))
        self.results_dir = os.path.join(base_path, "search_results")
        os.makedirs(self.results_dir, exist_ok=True)

    def tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text using regex, remove numbers, and preserve hyphenated words.
        """
        return [token for token in re.findall(r'\b\w+(?:-\w+)*\b', text.lower()) if any(c.isalpha() for c in token)]

    def expand_query_with_country_synonyms(self, query_tokens: List[str]) -> List[str]:
        """
        Expand query tokens with origin synonyms.
        """
        expanded_tokens = query_tokens.copy()
        for country, synonyms in self.origin_synonyms.items():
            if country in query_tokens:
                expanded_tokens.extend(synonyms)
            for synonym in synonyms:
                if synonym in query_tokens:
                    expanded_tokens.append(country)
                    expanded_tokens.extend(
                        [s for s in synonyms if s != synonym])
        return list(set(expanded_tokens))

    def filter_documents_with_any_token(self, query_tokens: List[str]) -> Set[str]:
        """
        Filter documents that contain at least one query token.
        """
        matching_docs = set()

        for token in query_tokens:
            # Check all indexes for the token
            if token in self.title_index:
                matching_docs.update(self.title_index[token].keys())
            if token in self.description_index:
                matching_docs.update(self.description_index[token].keys())
            if token in self.brand_index:
                matching_docs.update(self.brand_index[token])
            if token in self.origin_index:
                matching_docs.update(self.origin_index[token])

        return matching_docs

    def filter_documents_with_all_tokens(self, query_tokens: List[str]) -> Set[str]:
        """
        Filter documents that contain all query tokens (except stopwords).
        """
        if not query_tokens:
            return set()

        matching_docs = self.filter_documents_with_any_token([query_tokens[0]])

        for token in query_tokens[1:]:
            token_docs = self.filter_documents_with_any_token([token])
            matching_docs.intersection_update(token_docs)

        return matching_docs

    def exact_match_search(self, query: str) -> Set[str]:
        """
        Perform an exact match search.
        """
        normalized_query = query.lower().strip()
        matching_docs = set()

        for doc_url, product in self.products.items():
            # Title match
            if normalized_query == product['title'].lower().strip():
                matching_docs.add(doc_url)
            # Brand match
            if 'brand' in product and normalized_query == product['brand'].lower().strip():
                matching_docs.add(doc_url)
            # Origin match
            if 'product_features' in product and 'made in' in product['product_features']:
                if normalized_query == product['product_features']['made in'].lower().strip():
                    matching_docs.add(doc_url)

        return matching_docs

    def compute_bm25_score(self, doc_url: str, query_tokens: List[str], k1: float = 1.5, b: float = 0.75) -> float:
        """
        Calculate BM25 score for a document.
        """
        score = 0
        doc = self.products[doc_url]
        doc_text = f"{doc['title']} {doc['description']}"
        doc_tokens = self.tokenize_text(doc_text)

        # Document length normalization
        avg_doc_length = 300  # Approximate average document length
        doc_length = len(doc_tokens)

        for token in query_tokens:
            # Calculate term frequency in document
            tf = doc_tokens.count(token)

            # Calculate inverse document frequency
            doc_count = len(self.title_index.get(token, {})) + \
                len(self.description_index.get(token, {}))
            if doc_count == 0:
                continue

            idf = math.log(
                (len(self.products) - doc_count + 0.5) / (doc_count + 0.5))

            # Calculate BM25 score for this term
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))
            score += idf * (numerator / denominator)

        return score

    def compute_ranking_score(self, doc_url: str, query: str, query_tokens: List[str]) -> Dict[str, float]:
        """
        Calculate final ranking score combining multiple signals
        Returns both final score and individual component scores for transparency.
        
        """
        doc = self.products[doc_url]
        scores = {
            'bm25_score': 0,
            'exact_match_score': 0,
            'review_score': 0,
            'title_match_score': 0,
            'origin_match_score': 0
        }

        # 1. BM25 score (40% weight)
        scores['bm25_score'] = self.compute_bm25_score(doc_url, query_tokens) * 0.4

        # 2. Exact match bonus (fixed score of 2.0)
        if (query.lower().strip() == doc['title'].lower().strip() or
            ('brand' in doc and query.lower().strip() == doc['brand'].lower().strip()) or
            ('product_features' in doc and 'made in' in doc['product_features'] and
             query.lower().strip() == doc['product_features']['made in'].lower().strip())):
            scores['exact_match_score'] = 2.0

        # 3. Review score (30% weight)
        if doc_url in self.reviews_index:
            review_data = self.reviews_index[doc_url]
            base_review_score = (review_data['mean_mark'] * 0.3 +
                                 min(review_data['total_reviews'], 10) * 0.1)
            scores['review_score'] = base_review_score * 0.3

        # 4. Title match score (20% weight)
        title_tokens = self.tokenize_text(doc['title'])
        title_matches = sum(
            1 for token in query_tokens if token in title_tokens)
        scores['title_match_score'] = title_matches * 0.2

        # 5. Origin match score (10% weight)
        if 'product_features' in doc and 'made in' in doc['product_features']:
            origin = doc['product_features']['made in'].lower()
            if origin in query_tokens:
                scores['origin_match_score'] = 0.1

        # Calculate final score
        scores['final_score'] = sum(scores.values())
        return scores

    def _save_search_results(self, results: Dict) -> None:
        """
        Save search results to a JSON file.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        query_slug = re.sub(r'[^a-z0-9]+', '_',
                            results['metadata']['query'].lower())
        filename = f"search_{query_slug}_{timestamp}.json"
        filepath = os.path.join(self.results_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    def search(self, query: str, search_type: str = 'any', save_results: bool = False) -> Dict:
        """
        Main search function with different search types and optional result saving.

        Parameters:
        - query: Search query string.
        - search_type: Type of search ('any', 'all', or 'exact').
        - save_results: Whether to save results to a JSON file (default: False).
        """
        # Tokenize and normalize query
        query_tokens = self.tokenize_text(query)
        query_tokens = [
            token for token in query_tokens if token not in STOPWORDS]
        expanded_tokens = self.expand_query_with_country_synonyms(query_tokens)

        # Get matching documents based on search type
        if search_type == 'exact':
            matching_docs = self.exact_match_search(query)
        elif search_type == 'all':
            matching_docs = self.filter_documents_with_all_tokens(expanded_tokens)
        else:  # 'any'
            matching_docs = self.filter_documents_with_any_token(expanded_tokens)

        # Rank documents with detailed scores
        ranked_docs = []
        for doc_url in matching_docs:
            scores = self.compute_ranking_score(
                doc_url, query, expanded_tokens)
            doc = self.products[doc_url]
            ranked_docs.append({
                'title': doc['title'],
                'url': doc_url,
                'description': doc['description'],
                'scores': scores,
                'score': round(scores['final_score'], 3)
            })

        # Sort by final score
        ranked_docs.sort(key=lambda x: x['score'], reverse=True)

        # Prepare results
        results = {
            'metadata': {
                'query': query,
                'search_type': search_type,
                'timestamp': datetime.now().isoformat(),
                'total_documents': len(self.products),
                'filtered_documents': len(matching_docs)
            },
            'results': ranked_docs
        }

        # Save results if requested
        if save_results:
            self._save_search_results(results)

        return results

if __name__ == "__main__":
    # Initialize search engine
    search_engine = SearchEngine()

    # Example queries for testing
    test_queries = [
        "box of chocolate candy",
        "black shirt",
        "american made products",
        "high rated items"
    ]

    # Test each query with all search types
    search_types = ['all', 'exact', 'any',]

    for query in test_queries:
        print(f"\nTesting query: {query}")
        for search_type in search_types:
            print(f"\nSearch type: {search_type}")
            results = search_engine.search(
                query, search_type, save_results=True)
            print(
                f"Found {results['metadata']['filtered_documents']} documents")
            for i, doc in enumerate(results['results'][:3], 1):
                print(f"\n{i}. {doc['title']} (Score: {doc['score']})")
                print(f"URL: {doc['url']}")
                for component, score in doc['scores'].items():
                    if component != 'final_score':
                        print(f"  - {component}: {score:.3f}")
                if doc['description']:
                    print(f"Description: {doc['description'][:200]}...")
