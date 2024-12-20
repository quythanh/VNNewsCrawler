import requests
import sys
from pathlib import Path

from bs4 import BeautifulSoup

from models import Article

from .base_crawler import BaseCrawler
from logger import log
from utils import get_text_from_tag

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH


class DanTriCrawler(BaseCrawler):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.logger = log.get_logger(name=__name__)
        self.base_url = "https://dantri.com.vn"
        self.article_type_dict = {
            0: "xa-hoi",
            1: "the-gioi",
            2: "kinh-doanh",
            3: "bat-dong-san",
            4: "the-thao",
            5: "lao-dong-viec-lam",
            6: "tam-long-nhan-ai",
            7: "suc-khoe",
            8: "van-hoa",
            9: "giai-tri",
            10: "suc-manh-so",
            11: "giao-duc",
            12: "an-sinh",
            13: "phap-luat"
        }

    def extract_content(self, url: str) -> Article:
        """
        Extract title, description and paragraphs from url
        @param url (str): url to crawl
        @return title (str)
        @return description (generator)
        @return paragraphs (generator)
        """
        content = requests.get(url).content
        soup = BeautifulSoup(content, "html.parser")

        title = soup.find("h1", class_="title-page detail") 
        if title is None:
            return None
        title = title.text

        description = (get_text_from_tag(p) for p in soup.find("h2", class_="singular-sapo").contents)
        content = soup.find("div", class_="singular-content")
        paragraphs = (get_text_from_tag(p) for p in content.find_all("p"))

        article = Article(title, description, paragraphs, url, None)

        return article

    def get_urls_of_type_thread(self, article_type, page_number):
        """" Get urls of articles in a specific type in a page"""
        page_url = f"https://dantri.com.vn/{article_type}/trang-{page_number}.htm"
        content = requests.get(page_url).content
        soup = BeautifulSoup(content, "html.parser")
        titles = soup.find_all(class_="article-title")

        if (len(titles) == 0):
            self.logger.info(f"Couldn't find any news in {page_url} \nMaybe you sent too many requests, try using less workers")

        articles_urls = list()

        for title in titles:
            link = title.find_all("a")[0]
            articles_urls.append(self.base_url + link.get("href"))

        return articles_urls

    def get_urls_of_search_thread(self, search_query, page_number) -> list:
        return super().get_urls_of_search_thread(search_query, page_number)
