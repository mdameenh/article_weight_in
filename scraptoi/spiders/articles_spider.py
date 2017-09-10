import scrapy, urlparse, os

from scrapy_splash import SplashRequest

class ArticleList(scrapy.Spider):
    name="articles"
    globcnt = 0
    start_urls = ["http://timesofindia.indiatimes.com/archive.cms"]
    
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='render.html', args={'wait':0.5})
    
    def parse(self, response):
        f = open('data/yearmonth/l1.csv', 'w')
        urls = []
        for month in response.css("a.normtxt::attr('href')").extract():
            if month.endswith(".cms"):
                t_url = urlparse.urljoin("http://timesofindia.indiatimes.com/", month)
                year = "%04d" % (int((month.split("/")[2].split(",")[0].split("-")[1].strip())))
                month = "%02d" % (int(month.split("/")[2].split(",")[1].split("-")[1].replace(".cms", "").strip()))
                if int(year)>=2007 and int(month) <= 12:
                    f.write("%s\t%s\t%s\n" % (t_url, year, month))
                    urls.append(t_url)
        f.close()
        f = open('data/yearmonth/l2.csv', 'w').close()
        
        for url in urls:
            SplashRequest(url, self.parse_l2, 
                                endpoint='render.html', 
                                args={'wait':0.5, 'timeout':20})
    
    
    def parse_l2(self, response):
        print("Blah")
        filepath = os.path.join('data/html_dump', str(self.globcnt)+'.html')
        with open(filepath, 'w') as f:
            f.write(response.body)
