from crawler import Crawler

if __name__ == '__main__':
    url = input("Enter your url: ")
    depth = int(input("Enter depth: "))
    crawler = Crawler(url, depth)
    crawler.crawl()
