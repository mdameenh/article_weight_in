import scrapy, urlparse

from scrapy_splash import SplashRequest

class ArticleList(scrapy.Spider):
    name="articles"
    start_urls = ["http://timesofindia.indiatimes.com/archive.cms"]
    
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='render.html', args={'wait':0.5})
    
    def parse(self, response):
        for month in response.css("a.normtxt::attr('href')").extract():
            if month.endswith(".cms"):
                t_link = urlparse.urljoin("http://timesofindia.indiatimes.com/", month)
                year = "%04d" % (int((month.split("/")[2].split(",")[0].split("-")[1].strip())))
                month = "%02d" % (int(month.split("/")[2].split(",")[1].split("-")[1].replace(".cms", "").strip()))
                yield{
                    'year' : year,
                    'month' : month,
                    'articlepath' : t_link
                    }
