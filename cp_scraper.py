import json
import time
import os
from urllib.parse import urljoin
import re

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from novel import load_data

novels = load_data()  # Dict[str, Novel]
BASE = "https://www.gongzicp.com/"

def fetch_rendered(url, timeout=15000):
	"""Use Playwright to render the page and return HTML, or None if unavailable."""
	try:
		with sync_playwright() as pw:
			browser = pw.chromium.launch(headless=True)
			page = browser.new_page()
			page.goto(url, timeout=timeout)

			# wait for network to be idle (shorter cap)
			try:
				page.wait_for_load_state("networkidle", timeout=min(timeout, 10000))
			except Exception:
				pass

			html = page.content()
			browser.close()
			return html
	except Exception:
		return None

def scrape_page(html):
	soup = BeautifulSoup(html, "html.parser")
	page_items = []

	container = soup.find(class_="novel-list")
	if not container:
		# fallback: search the whole document
		items = soup.find_all(class_="items")
	else:
		items = container.find_all(class_="items")

	for item in items:
		# link and name
		name_el = item.find("a", class_=lambda x: x and "novel-name" in x)
		link = ""
		name = ""
		if name_el and name_el.get("href"):
			href = name_el.get("href").strip()
			if re.search(r"novel-\d+\.html$", href):
				link = href if href.startswith("http") else urljoin(BASE, href)
			name = name_el.get_text(strip=True)

		# info/summary
		info_el = item.find("p", class_="novel-info")
		summary = info_el.get_text(" ", strip=True) if info_el else ""

		# author
		author_el = item.find("a", class_=lambda x: x and "novel-author" in x)
		author = author_el.get_text(strip=True) if author_el else ""

		# tags (skip link to ranking page)
		tags = []
		tag_list = item.find(class_="tag-list")
		if tag_list:
			for a in tag_list.find_all("a", class_=lambda x: x and "tag" in x):
				text = a.get_text(strip=True)
				if text:
					tags.append(text)

		if link:
			page_items.append({
				"link": link,
				"name": name,
				"summary": summary,
				"author": author,
				"tags": tags,
			})
	
	return page_items


def save_results(data, out_path):
	with open(out_path, "w", encoding="utf-8") as fh:
		json.dump(data, fh, ensure_ascii=False, indent=2)
	print(f"Saved links to {out_path}")


def main(base_url, type, pages):
	out_dir = os.path.join(os.path.dirname(__file__), type, "cp")
	os.makedirs(out_dir, exist_ok=True)
	
	session = requests.Session()
	session.headers.update(
		{
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36"
		}
	)
	page_items = []
	for page in range(1, pages + 1):
		url = f"{base_url}&page={page}"
		print(f"Fetching page {page}: {url}")
		try:
			html = fetch_rendered(url)
		except Exception as e:
			print(f"  Failed to fetch page {page}: {e}")
			continue

		if not html:
			print(f"  Empty response for page {page}, skipping")
			continue

		page_items.extend(scrape_page(html))
		if page % 5 == 0:  # Save every 5 pages
			out = os.path.join(out_dir, f"novels_cp_{page}.json")
			save_results(page_items, out)
			page_items = []  # reset for next batch
	
	# Save any remaining items after the loop
	if page_items:
		out = os.path.join(out_dir, f"novels_cp_{pages}.json")
		save_results(page_items, out)


if __name__ == "__main__":
	for type, novel in novels.items():
	    main(novel.cp, type, pages=novel.cp_page)
