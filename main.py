from crawler import Crawler
import asyncio

if __name__ == '__main__':
    url = input("Enter your url: ")
    depth = int(input("Enter depth: "))
    time_limit = int(input("Enter the time limit (in seconds): "))
    crawler = Crawler(url, depth, time_limit)
    asyncio.run(crawler.crawl())
