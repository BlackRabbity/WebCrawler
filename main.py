from crawler import Crawler

if __name__ == '__main__':
    url = input("Enter your url: ")
    depth = int(input("Enter depth: "))
    time_limit = int(input("Enter the time limit (in seconds): "))
    is_dfs = bool(input("bfs (0)/dfs (1): "))
    crawler = Crawler(url, depth, time_limit, is_dfs)
    crawler.crawl()
