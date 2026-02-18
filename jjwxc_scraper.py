"""
This file is adapted from:
Source: https://github.com/dev-chenxing/jjwxc-scraper/blob/main/jjwxc_scraper.py
Original Author: dev-chenxing (https://github.com/dev-chenxing)

Modified by: EITD
Date: 2026-02-09
Description: Keep extracting novel metadata from jjwxc.net, but remove the chapter details. The output JSON will contain a list of novels with their metadata, but no chapter information.
"""
import os
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urlparse, parse_qs
from novel import load_data


def clean_text(text):
    return " ".join(text.replace("\r", " ").replace("\n", " ").split())

novels = load_data() # Dict[str, Novel]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_novel_links(url):
    response = requests.get(url, headers=HEADERS)
    response.encoding = 'utf-8'
    markup = response.text
    soup = BeautifulSoup(markup, "html.parser")

    # Select all rows except the header
    rows = soup.select("tbody tr")[1:]

    novel_links = []
    for row in rows:
        # Get word count from 5th column
        word_count_td = row.select_one("td:nth-of-type(5)")

        try:
            # Extract and convert word count text to integer
            word_count = int(word_count_td.text.strip())
        except (AttributeError, ValueError):
            # Skip if word count is missing or invalid
            continue

        # Filter condition: only include novels with >= 20,000 words
        if word_count < 20000:
            continue

        # Get the <a> tag in the second column (作品 column)
        novel_link_tag = row.select_one("td:nth-of-type(2) a")
        if novel_link_tag and "onebook.php" in novel_link_tag["href"]:
            full_url = f"https://www.jjwxc.net/{novel_link_tag['href']}"
            novel_links.append(full_url)

    return novel_links


def get_novel_id(url):
    """Extract novel ID from URL"""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get('novelid', ['unknown'])[0]


def scrape_novel(url):
    print(f"Processing novel: {url}")
    response = requests.get(url, headers=HEADERS)
    response.encoding = "gbk"
    markup = response.text
    soup = BeautifulSoup(markup, "html.parser")
    # Extract novel metadata
    novel = {
        "url": url,
        "id": get_novel_id(url),
        "title": soup.find("h1", itemprop="name").find("span").text.strip(),
        "author": soup.find("h2").find("a").text.strip(),
        "genre": soup.find("span", itemprop="genre").text.strip(),
        "brief_intro": "",  # 一句话简介
        "tags": [
            a.text for a in soup.select('div.smallreadbody span > a[style*="red"]')
        ],  # 内容标签
        "characters": [],  # 主角
        "themes": "",  # 立意
        "summary": clean_text(
            soup.find("div", id="novelintro").get_text(separator="\n").strip()
        ),  # 文案
        "status": soup.find("span", itemprop="updataStatus").text.strip(),
        "word_count": soup.find("span", itemprop="wordCount").text.strip(),
        "collected_count": soup.find(
            "span", itemprop="collectedCount"
        ).text.strip(),
        "chapters": [],
        "latest_update": None,
    }

    # Extract 一句话简介
    brief_span = soup.find(
        'span', string=lambda text: text and '一句话简介' in text)
    if brief_span:
        # Extract text after "一句话简介："
        novel["brief_intro"] = brief_span.text.split('：', 1)[-1].strip()

    # Characters (主角)
    characters = soup.find_all('div', class_='character_name')
    novel['characters'] = [c.text.strip()
                           for c in characters if c.text.strip()]

    # Themes (立意)
    themes_span = soup.find('span', string=lambda t: t and '立意' in t)
    if themes_span:
        novel['themes'] = themes_span.text.split('：', 1)[-1].strip()

    # Select all rows except the header
    rows = soup.select('tr[itemprop~="chapter"]')
    for row in rows:
        cols = row.find_all("td")

        update_time = cols[-1].find("span").text.strip()
        # Check if this is the latest chapter
        if "newestChapter" in row["itemprop"]:
            novel["latest_update"] = update_time

        if len(cols) < 6:
            continue  # Skip VIP chapters

        if not cols[1].find("a", itemprop="url"):
            continue  # Skip 等待进入网审 chapters

    print(f"Scraped {novel['title']}")

    return novel


def main(base_url, type, pages):
    out_dir = os.path.join(os.path.dirname(__file__), type, "jj")
    os.makedirs(out_dir, exist_ok=True)

    for page_num in range(1, pages + 1):
        url = f"{base_url}&page={page_num}"
        novels = []
        try:
            print(f"Scraping page {page_num}/{pages}...")
            novel_links = get_novel_links(url)
            for link in novel_links:
                try:
                    novel_data = scrape_novel(link)
                    novels.append(novel_data)
                except Exception as e:
                    print(f"Error processing novel {link}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error scraping page {page_num}: {str(e)}")
            continue
        out_path = os.path.join(out_dir, f"novels_jj_{page_num}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(novels, f, ensure_ascii=False, indent=2)

    print(f"Scraping completed. Data saved to {out_dir}")

if __name__ == "__main__":
    for type, novel in novels.items():
        main(novel.jj, type, pages=novel.jj_page)
