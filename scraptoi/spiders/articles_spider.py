import scrapy, urlparse, json, os

from scrapy.http.headers import Headers
from scrapy_splash import SplashRequest

RENDER_HTML_URL = "http://127.0.0.1:8050/render.html"

class ArticleList(scrapy.Spider):
    name="articles"
    start_urls = ["http://timesofindia.indiatimes.com/archive.cms"]
    
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='render.html', args={'wait':0.5})
    
    def parse(self, response):
        f = open('data/yearmonth/l1.csv', 'w')
        headers = Headers({'Content-Type': 'application/json'})
        for month in response.css("a.normtxt::attr('href')").extract():
            if month.endswith(".cms"):
                t_url = urlparse.urljoin("http://timesofindia.indiatimes.com/", month)
                year = "%04d" % (int((month.split("/")[2].split(",")[0].split("-")[1].strip())))
                month = "%02d" % (int(month.split("/")[2].split(",")[1].split("-")[1].replace(".cms", "").strip()))
                if int(year)>=2017 and int(month) <= 2:
                    f.write("%s\t%s\t%s\n" % (t_url, year, month))
                    body = json.dumps({"url":t_url, "wait":0.5}, sort_keys=True)
                    yield scrapy.Request(RENDER_HTML_URL, self.parse_l2, method="POST",
                                         body=body, headers=headers)
        f.close()
    
    def parse_l2(self, response):
        #url_dates = []
        calendertable = response.css('table[id="calender"]')
        urllist = calendertable.css('a::attr("href")').extract()
        urllist = list(set(urllist))
        f = open('data/yearmonth/l2.csv', 'a')
        for url in urllist:
            url = urlparse.urljoin("http://timesofindia.indiatimes.com/", url)
            f.write("%s\n" % (url))
            request = scrapy.Request(url, self.parse_l3)
            t_url = url.split("/")
            request.meta['date'] = "".join(["%04d"% (int(t_url[3])), "%02d" % (int(t_url[4])), "%02d" % (int(t_url[5]))])
            yield request
            
                                 
    def parse_l3(self, response):
        article_table = response.css('table.cnt[border="0"]')
        article_td = article_table.css('td[width="670"]')
        article_urls = article_td.css('a[href*="articleshow"]').extract()
        article_texts = article_td.css('a[href*="articleshow"]::text').extract()
        
        curr_dir = os.path.join("data/articles", response.meta['date'])
        os.makedirs(curr_dir)
        f = open(os.path.join(curr_dir, response.meta['date']+"_urls.csv"), 'a')
        p = open(os.path.join(curr_dir, response.meta['date']+"_articles.csv"), 'a')

        for url in article_urls:
            f.write("%s\n" % (url.encode('UTF-8')))
            
        for article in article_texts:
            p.write("%s\n" % (article.encode('UTF-8')))
        
    def parse_article(self, response):
        pass

