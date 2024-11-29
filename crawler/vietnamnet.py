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


class VietNamNetCrawler(BaseCrawler):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.logger = log.get_logger(name=__name__)
        self.base_url = "https://vietnamnet.vn"
        self.article_type_dict = {
            0: "thoi-su",
            1: "kinh-doanh",
            2: "the-thao",
            3: "van-hoa",
            4: "giai-tri",
            5: "the-gioi",
            6: "doi-song",
            7: "giao-duc",
            8: "suc-khoe",
            9: "thong-tin-truyen-thong",
            10: "phap-luat",
            11: "oto-xe-may",
            12: "bat-dong-san",
            13: "du-lich",
        }

    def extract_content(self, url: str) -> tuple:
        """
        Extract title, description and paragraphs from url
        @param url (str): url to crawl
        @return title (str)
        @return description (generator)
        @return paragraphs (generator)
        """
        content = requests.get(url).content
        soup = BeautifulSoup(content, "html.parser")

        title_tag = soup.find("h1", class_="content-detail-title") 
        desc_tag = soup.find("h2", class_=["content-detail-sapo", "sm-sapo-mb-0"])
        p_tag = soup.find("div", class_=["maincontent", "main-content"])

        if [var for var in (title_tag, desc_tag, p_tag) if var is None]:
            return None, None, None

        title = title_tag.text
        description = (get_text_from_tag(p) for p in desc_tag.contents)
        paragraphs = (get_text_from_tag(p) for p in p_tag.find_all("p"))

        return title, description, paragraphs

    def get_urls_of_type_thread(self, article_type, page_number):
        """" Get urls of articles in a specific type in a page"""
        page_url = f"https://vietnamnet.vn/{article_type}-page{page_number}"
        content = requests.get(page_url).content
        soup = BeautifulSoup(content, "html.parser")
        titles = soup.find_all(class_=["horizontalPost__main-title", "vnn-title", "title-bold"])

        if (len(titles) == 0):
            self.logger.info(f"Couldn't find any news in {page_url} \nMaybe you sent too many requests, try using less workers")

        articles_urls = list()

        for title in titles:
            full_url = title.find_all("a")[0].get("href")
            if self.base_url not in full_url:
                full_url = self.base_url + full_url
            articles_urls.append(full_url)

        return articles_urls

    def get_urls_of_search_thread(self, search_query, page_number) -> list:
        return super().get_urls_of_search_thread(search_query, page_number)
