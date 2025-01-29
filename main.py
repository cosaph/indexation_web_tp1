from crawler import crawl

if __name__ == "__main__":
    start_url = "https://web-scraping.dev/products"
    crawled = crawl(start_url)
    #print(f"URLs Crawled: {len(crawled)}")
