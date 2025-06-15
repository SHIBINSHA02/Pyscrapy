import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import quote_plus

scraped_items = []

class FlipkartSpider(scrapy.Spider):
    name = 'flipkart'
    allowed_domains = ['flipkart.com']
    
    def __init__(self, product_name='laptop', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [
            f'https://www.flipkart.com/search?q={quote_plus(product_name)}&page=1'
        ]

    def parse(self, response):
        products = response.xpath('//div[contains(@class, "_1AtVbE")]')
        
        for product in products:
            item = {
                'name': product.xpath('.//div[contains(@class, "_4rR01T") or contains(@class, "s1Q9rs")]/text()').get(),
                'price': product.xpath('.//div[contains(@class, "_30jeq3")]//text()').get(),
                'rating': product.xpath('.//div[contains(@class, "_3LWZlK")]/text()').get(),
                'link': response.urljoin(product.xpath('.//a[contains(@href, "/p/")]/@href').get())
            }
            if all(item.values()):
                item['name'] = item['name'].strip() if item['name'] else None
                item['price'] = item['price'].replace('₹', '').strip() if item['price'] else None
                item['rating'] = float(item['rating'].strip()) if item['rating'] else None
                scraped_items.append(item)  # Store in global list

        next_page = response.xpath('//a[contains(., "Next")]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'LOG_LEVEL': 'INFO'
    })
    process.crawl(FlipkartSpider, product_name='laptop')
    process.start()
    # Now scraped_items contains all the results
    print("\nAll Scraped Items:")
    for item in scraped_items:
        print(item)
