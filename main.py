from crawler import Crawler

if __name__ == '__main__':
    url = input("Enter your url: ")
    crawler = Crawler(url, 2)
    crawler.crawl()
