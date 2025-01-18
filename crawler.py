import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import networkx as nx
import matplotlib.pyplot as plt
import itertools

class Crawler:

    def __init__(self, start_url, depth):
        self.depth = depth
        self.tree = nx.DiGraph()
        self.start_url = start_url
        self.visited = set()

    def fetch_url(self, url):
        print(f"Fetching: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Cannot fetch URL: {url}")
            return ""

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def bfs_dfs_search(self, is_dfs):
        q = [(self.start_url, 0)]
        self.visited.add(self.start_url)
        while q:
            if is_dfs:
                curr, curr_depth = q.pop()
            else:
                curr, curr_depth = q.pop(0)

            if self.depth < curr_depth:
                continue

            if not self.tree.has_node(curr):
                self.tree.add_node(curr)

            links = itertools.islice(self.get_linked_urls(curr, self.fetch_url(curr)), 10)

            for link in links:
                if link not in self.visited:
                    self.visited.add(link)
                    q.append((link, curr_depth + 1))
                    self.tree.add_edge(curr, link)



    def print_tree(self):
        pos = nx.spring_layout(self.tree)
        plt.figure(figsize=(12, 8))
        nx.draw(
            self.tree,
            pos,
            with_labels=True,
            node_size=300,
            node_color="lightblue",
            font_size=6,
            font_weight="bold",
            font_color="black",
        )
        plt.title(f"Web Crawler Tree")
        plt.show()

    def crawl(self):
        self.bfs_dfs_search(False)
        self.print_tree()
