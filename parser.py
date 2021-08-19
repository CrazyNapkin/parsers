import logging
import requests
import bs4
import collections
import csv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')

ParserResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url',
    ),
)

HEADERS = (
    'Brands name',
    'Goods name',
    'URL',
)
class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0"
}
        self.result = []

    def load_page(self, page: int = None):
        url = 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/vodolazki'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.dtList.i-dtList.j-card-item')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        # logger.info(block)
        # logger.info('=' * 100)
        
        url_block = block.select_one('a.ref_goods_n_p')
        if not url_block:
            logger.error('no url_block')
            return
        
        url = url_block.get('href')
        if not url:
            logger.error('no href')
            return
        
        brand_name = block.select_one('div.dtlist-inner-brand-name')
        if not brand_name:
            logger.error(f'no name_block on{url}')
            return
        #Wrangler
        brand_name = brand_name.text
        brand_name = brand_name.replace('/','').strip()

        goods_name = block.select_one('span.goods-name')
        if not goods_name:
            logger.error(f'no goods_name on {url}')
            return
        #Wrangler
        goods_name = goods_name.text
        goods_name = goods_name.replace('/','').strip()

        

        self.result.append(ParserResult(
            url=url,
            brand_name=brand_name,
            goods_name=goods_name,
        ))
        

        
        logger.debug('%s, %s , %s', url, brand_name,goods_name)
        logger.debug('='*100)

        
    def save_results(self):
        path = '/home/aidos/python projects/practice/parser_test/results.csv'
        with open(path,'w') as f:
            writer = csv.writer(f,quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)


    def run(self):
        text = self.load_page()
        self.parse_page(text=text)
        logger.info(f'Received {len(self.result)} elements')
        self.save_results()


if __name__ == '__main__':
    parser = Client()
    parser.run()

