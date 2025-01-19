import requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urljoin
import networkx as nx
from pyvis.network import Network
import time
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
#from stem.control import Controller
#from stem import Signal


class Crawler:

    def __init__(self, start_url, depth, time_limit):
        self.depth = depth
        self.tree = nx.DiGraph()
        self.start_url = start_url
        self.visited = set()
        self.time_limit = time_limit
        self.start_time = time.time()
        self.max_threads = 10
        self.webs_content = [{"url": "URL", "text": "Extracted Text"}]
        self.lock = Lock()
        #self.session = self.set_tor_proxy()

    def set_tor_proxy(self):
        session = requests.Session()
        session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        response = session.get('https://check.torproject.org')
        return session

    def change_tor_ip(self):
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)

    def fetch_url(self, url):
        print(f"Fetching: {url}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Referer": "https://www.google.com/"
            }
            response = requests.get(url, timeout=5, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            self.webs_content.append({"url": url, "text": soup.get_text(strip=True)})
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Cannot fetch URL: {url}")
            return ""

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            path = link.get('href')
            #print(f"get linked urls: {path}")
            if not path or path.startswith(('#', 'javascript:', 'mailto:')):
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
                writer.writerow([obj['url'], obj['text']])

    def bfs_dfs_search(self, is_dfs):
        q = [(self.start_url, 0)]
        self.visited.add(self.start_url)
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            while (q or futures) and not self.is_time_up():
                while q and len(futures) < self.max_threads:
                    if is_dfs:
                        curr, curr_depth = q.pop()
                    else:
                        curr, curr_depth = q.pop(0)

                    if self.depth < curr_depth:
                        continue

                    if not self.tree.has_node(curr):
                        self.tree.add_node(curr)

                    futures.append(executor.submit(self._process_url, curr, curr_depth))

                for future in futures[:]:
                    if future.done():
                        results = future.result()
                        futures.remove(future)
                        if results:
                            for parent, child, child_depth in results:
                                with self.lock:
                                    if child not in self.visited:
                                        self.visited.add(child)
                                        q.append((child, curr_depth))
                                        self.tree.add_edge(parent, child)

        print("Task stopped !")

    def _process_url(self, url, depth):
        links = self.get_linked_urls(url, self.fetch_url(url))
        return [(url, link, depth + 1) for link in links]

    def print_tree(self):
        net = Network(height='800px', width='100%', directed=True)
        for node in self.tree.nodes:
            net.add_node(node, label=str(node))
        for edge in self.tree.edges:
            net.add_edge(edge[0], edge[1])
        #print(self.tree.nodes)

        for node in self.tree.nodes:
            try:
                net.get_node(node)['x'] = 0
                net.get_node(node)['y'] = 0
            except:
                print(f"Error printing node: {node}")
        net.force_atlas_2based()
        net.show("graph.html", notebook=False)

    def crawl(self):
        self.bfs_dfs_search(False)
        self.print_tree()
        self.save_to_csv("crawl.csv")
