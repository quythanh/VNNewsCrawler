import requests
import sys
from pathlib import Path

from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler
from ..logger import log
from ..utils.bs4_utils import get_text_from_tag

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH


class VNExpressCrawler(BaseCrawler):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.logger = log.get_logger(name=__name__)
        self.article_type_dict = {
            0: "thoi-su",
            1: "du-lich",
            2: "the-gioi",
            3: "kinh-doanh",
            4: "khoa-hoc",
            5: "giai-tri",
            6: "the-thao",
            7: "phap-luat",
            8: "giao-duc",
            9: "suc-khoe",
            10: "doi-song"
        }

    def extract_content(self, url: str) -> tuple[str, tuple[str], tuple[str]]:
        """
        Extract title, description and paragraphs from url
        @param url (str): url to crawl
        @return title (str)
        @return description (generator)
        @return paragraphs (generator)
        """
        try:
            content = requests.get(url).content
        except Exception:
            return None, None, None
        soup = BeautifulSoup(content, "html.parser")

        title = soup.find("h1", class_="title-detail") 
        if title is None:
            return None, None, None
        title = title.text

        # some sport news have location-stamp child tag inside description tag
        description = (get_text_from_tag(p) for p in soup.find("p", class_="description").contents)
        paragraphs = (get_text_from_tag(p) for p in soup.find_all("p", class_="Normal"))

        return title, description, paragraphs

    def get_urls_of_type_thread(self, article_type, page_number):
        """" Get urls of articles in a specific type in a page"""
        page_url = f"https://vnexpress.net/{article_type}-p{page_number}"
        content = requests.get(page_url).content
        soup = BeautifulSoup(content, "html.parser")
        titles = soup.find_all(class_="title-news")

        if (len(titles) == 0):
            self.logger.info(f"Couldn't find any news in {page_url} \nMaybe you sent too many requests, try using less workers")

        articles_urls = list()

        for title in titles:
            link = title.find_all("a")[0]
            articles_urls.append(link.get("href"))

        return articles_urls

    def get_urls_of_search_thread(self, search_query, page_number):
        """
        Fetch URLs of articles for a given search query and page number.

        @param search_query (str): The search query.
        @param page_number (int): The page number to crawl.

        @return articles_urls (list): List of article URLs from the search result page.
        """
        page_url = f"https://timkiem.vnexpress.net/?q={search_query}&media_type=text&fromdate=0&todate=0&latest=on&cate_code=&search_f=title,tag_list&date_format=all&page={page_number}"
        content = requests.get(page_url).content
        soup = BeautifulSoup(content, "html.parser")
        titles = soup.find_all(class_="title-news")

        if len(titles) == 0:
            self.logger.info(f"Couldn't find any news in {page_url} \nMaybe you sent too many requests, try using less workers")

        articles_urls = list()

        for title in titles:
            link = title.find_all("a")[0]
            articles_urls.append(link.get("href"))

        return articles_urls
