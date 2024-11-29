from .dantri import DanTriCrawler
from .vietnamnet import VietNamNetCrawler
from .vnexpress import VNExpressCrawler

WEBNAMES = {"vnexpress": VNExpressCrawler,
            "dantri": DanTriCrawler,
            "vietnamnet": VietNamNetCrawler}

def get_crawler(webname, **kwargs):
    crawler = WEBNAMES[webname](**kwargs)
    return crawler
