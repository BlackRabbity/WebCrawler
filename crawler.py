import requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urljoin
import networkx as nx
import matplotlib.pyplot as plt
import itertools
import time
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

class Crawler:

    def __init__(self, start_url, depth, time_limit):
        self.depth = depth
        self.tree = nx.DiGraph()
        self.start_url = start_url
        self.visited = set()
        self.time_limit = time_limit
        self.start_time = time.time()
        self.webs_content = [{"url": "URL", "text": "Extracted Text"}]

    def fetch_url(self, url):
        print(f"Fetching: {url}")
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            # soup_body = str(soup.body).replace("\n", "\\n").strip()
            self.webs_content.append({"url": url, "text": soup.get_text(strip=True)})
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Cannot fetch URL: {url}")
            return ""

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            path = link.get('href')
            if not path or path.startswith('#') or path.startswith('javascript:') or path.startswith('mailto:'):
                continue
            if path.startswith('/'):
                path = urljoin(url, path)
                encoded_path = urllib.parse.quote(path, safe=':/?&=.#')
            yield encoded_path

    def is_time_up(self):
        current_time = time.time()

        if current_time - self.start_time > self.time_limit:
            print("Time limit reached !")
            return True
        return False

    def save_to_csv(self, filename="output.csv"):
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            for obj in self.webs_content:
                writer.writerow([obj['url'],obj['text']])

    def bfs_dfs_search(self, is_dfs):
        q = [(self.start_url, 0)]
        self.visited.add(self.start_url)
        with ThreadPoolExecutor() as executor:
            while not self.is_time_up() and q:
                if is_dfs:
                    curr, curr_depth = q.pop()
                else:
                    curr, curr_depth = q.pop(0)

                if self.depth < curr_depth:
                    continue

                if not self.tree.has_node(curr):
                    self.tree.add_node(curr)

                links = self.get_linked_urls(curr, self.fetch_url(curr))

                futures = []
                for link in links:
                    if link not in self.visited:
                        self.visited.add(link)
                        q.append((link, curr_depth + 1))
                        self.tree.add_edge(curr, link)
                        futures.append(executor.submit(self.fetch_url, link))

                for future in as_completed(futures):
                    result = future.result()

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

    def crawl(self):
        self.bfs_dfs_search(True)
        self.print_tree()
        self.save_to_csv("crawl.csv")
