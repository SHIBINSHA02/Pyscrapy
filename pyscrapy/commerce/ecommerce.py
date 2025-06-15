import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import quote_plus
import requests
from lxml import html as lxml_html

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"  # Use the model you have

def get_main_xpath_from_llama(page_html):
    prompt = (
        "Given the following HTML, extract the main XPath that contains the list of product cards. "
        "Only reply with the XPath, nothing else.\n\n"
        f"{page_html[:10000]}"
    )
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        })
       if response.ok:
        data = response.json()
    xpath = data.get('response') or data.get('message') or ''
    # Remove code fences and whitespace
    xpath = xpath.replace('```
    if xpath and (xpath.startswith('/') or xpath.startswith('.')):
        return xpath
    else:
        print("Invalid XPath received from Llama:", xpath)
        return None
        else:
            print("Failed to get XPath from Llama:", response.text)
            return None
    except Exception as e:
        print("Error communicating with Ollama:", e)
        return None


class FlipkartSpider(scrapy.Spider):
    name = 'flipkart'
    allowed_domains = ['flipkart.com']

    def __init__(self, product_name='laptop', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [
            f'https://www.flipkart.com/search?q={quote_plus(product_name)}&page=1'
        ]
        self.xpath = None

    def parse(self, response):
        page_html = response.text
        self.xpath = get_main_xpath_from_llama(page_html)
        if not self.xpath:
            self.logger.error("Could not get XPath from Llama. Exiting.")
            return

        tree = lxml_html.fromstring(page_html)
        products = tree.xpath(self.xpath)
        for product in products:
            name = product.xpath('.//div[contains(@class, "_4rR01T") or contains(@class, "s1Q9rs")]/text()')
            price = product.xpath('.//div[contains(@class, "_30jeq3")]/text()')
            rating = product.xpath('.//div[contains(@class, "_3LWZlK")]/text()')
            link = product.xpath('.//a[contains(@href, "/p/")]/@href')

            # Extract values safely
            item = {
                'name': name.strip() if name else None,
                'price': price.replace('₹', '').strip() if price else None,
                'rating': None,
                'link': response.urljoin(link) if link else None
            }
            # Parse rating safely
            if rating and rating.strip():
                try:
                    item['rating'] = float(rating.strip())
                except Exception:
                    item['rating'] = None

            # Yield only if name and price are present (relax as needed)
            if item['name'] and item['price']:
                yield item

        next_page = tree.xpath('//a[contains(text(), "Next")]/@href')
        if next_page:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, callback=self.parse)

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'LOG_LEVEL': 'INFO'
    })
    process.crawl(FlipkartSpider, product_name='laptop')
    process.start()
