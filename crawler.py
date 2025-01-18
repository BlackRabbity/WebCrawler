import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import networkx as nx
import matplotlib.pyplot as plt
import itertools
import time
import csv
import pygraphviz as pgv

class Crawler:

    def __init__(self, start_url, depth, time_limit):
        self.depth = depth
        self.tree = nx.DiGraph()
        self.start_url = start_url
        self.visited = set()
        self.time_limit = time_limit
        self.start_time = time.time()

    def fetch_url(self, url):
        print(f"Fetching: {url}")
        try:
            response = requests.get(url, timeout=5)
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

    async def is_time_up(self):
        current_time = time.time()

        if current_time - self.start_time > self.time_limit:
            print("Time limit reached !")
            return True
        return False

    def save_to_csv(self, filename="output.csv"):
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["URL", "Extracted Text"])

            for url in self.visited:
                text = self._extract_text(url)
                writer.writerow([url, text])

    def _extract_text(self, url):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            return soup.get_text(strip=True)
        except requests.RequestException:
            return ""

    async def bfs_dfs_search(self, is_dfs):
        q = [(self.start_url, 0)]
        self.visited.add(self.start_url)
        while not await self.is_time_up() and q:
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
        print("Task stopped !")

    def print_tree(self):
        A = nx.nx_agraph.to_agraph(self.tree)
        A.layout(prog="dot")
        pos = {}
        for node in self.tree.nodes:
            x, y = A.get_node(node).attr['pos'].split(',')
            pos[node] = (float(x), float(y))

        #pos = {node: (x, -y) for node, (x, y) in pos.items()}

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
        plt.show()

    async def crawl(self):
        await self.bfs_dfs_search(False)
        self.print_tree()
        self.save_to_csv("crawl.csv")
