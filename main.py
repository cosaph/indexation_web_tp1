# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ccottet <ccottet@student.42.fr>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/01/30 16:33:51 by ccottet           #+#    #+#              #
#    Updated: 2025/01/30 16:39:33 by ccottet          ###   ########.fr        #
#                                                                              #
# **************************************************************************** #



from crawler import crawl

if __name__ == "__main__":
    start_url = "https://web-scraping.dev/products"
    crawled = crawl(start_url)
    #print(f"URLs Crawled: {len(crawled)}")
