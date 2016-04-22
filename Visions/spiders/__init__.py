"""
Scrape: Visions.ca

To run this script, in this directory, run 'scrapy crawl visions' in the
terminal.

For each category listed on the lefthand banner on the
http://www.visions.ca/Default.aspx page, this script will extract the
product details for one product.

For each run of the spider, a JSON file and log file are created, containing
the thirteen scraped products, one per category, and a log for the spider,
respectively. Each of thirteen categories are listed as a field for their
respective product.

"""
import re
from scrapy import Request, log
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.spiders import CrawlSpider
from Visions.items import VisionsProduct
from Visions.utils.xgroup import (
	XGroup, detailsRunner, extract_helper, price_to_float
)
from Visions.utils.helpers import add_schema

# Logs spider information to stdout
log.start()

class VisionSpider(CrawlSpider):
	name = 'visions'
	allowed_domains = ['visions.ca']
	start_urls = ['http://www.visions.ca/Default.aspx']

	MAIN_NAV_PATHS = (
		'//ul[contains(@id, "mastermenu-start")]//ul[contains(@id, '
		'"dropdown")]/li/a[not(contains(span/text(), "GIFT") or '
		'contains(span/text(), "more"))]/@href'
	)

	SUB_NAV_PATHS = (
		'//div[contains(@id, "subcatemenu-container")]/h2[1]/following-'
		'sibling::div[1]/ul/li/a/@href'
	)

	INNER_SUB_NAV_PATHS = (
		'//div[contains(@class,"breadCrumbs")]/a[last()]/@href'
	)

	ALT_SUB_NAV_PATHS = (
		'//div[contains(@id, "subcatemenu-brand")]/ul/li//div[contains'
		'(@class, "itembox")]/a/@href'
	)

	PRODUCT_PAGE_PATHS = (
		'//a[contains(@id, "ProductDetail")]/@href',
		'//div[@class="image"]/a/@href',
		'//div[@class="contentright"]/p/preceding-sibling::*/a/@href',
		'//div[contains(@id, "ProductName")]/a/@href',
		'//div[@class="productresult-imagebox"]/following-sibling::div'
		'[1]/h2/a/@href',
	)

	BUNDLE_PAGE_PATHS = (
		'//div[@class="bundleItem"]//td[@class="name"]/a/@href',
	)

	EMPTY_PAGE_CHECK = (
		'//*[@id="ctl00_tdMainPanel"]/div/div[@id="ctl00_Content'
		'PlaceHolder1_pnlNoRecords"]',
		'//div/span[contains(@class,"productpanel")]/text()[contains'
		'(.,"Featured Items")]'
	)

	CRUMB_TRAIL_PATHS = ('//div[@class="breadCrumbs"]/a')

	CRUMB_TRAIL_LABEL_PATHS = ('//div[@class="breadCrumbs"]/a/text()')

	PRODUCT_DETAILS = (
		XGroup(
			name='product',
			path=(
				'//div[contains(@class, "contentright")]/h2/a/font/text()',
				'//h1/span[contains(@id, "ProdTitle")]/text()',
				'div[contains(@class, "catalogueTitle")]/h3/text()',
				'//div[contains(@class,"Title")]/h3/text()',
				'//div[contains(@class,"Title")]//text()'
			),
			process=lambda x: x.strip() if x else None
		),
		XGroup(
			name='price',
			path=(
				'//div[contains(@class, "pricing")]//span//text()[1]',
				'//div[@class="productdetail-pricing"]/div/span[@id]/text()[1]',
				'//div[contains(@class, "contenctright")]/div/div/span'
				'[@class="price"]',
				'//div/span[contains(@id, "Saleprice")]/text()',
				'div[@id="ctl00_ContentPlaceHolder1_pnlBundle"]/div'
				'[@id="divProductDetails"]/div[contains(@class, '
				'"priceAddToCart")]/div[1]/span[contains(@id, "'
				'SalePrice")]/text()',
				'//div[@class="productdetail-pricing"]/div/span/text()'
				'[not(contains(.,"save"))][1]',
				'//div[@class="price"]/span[@class="salePrice"]/text()',
				'//div[contains(@class, "price")]/span[contains(@class, '
				'"Price")]//span[contains(text(), "$")][1]',
				'//div[@class="price"]/span[@class="regPrice"]/span/text()',
				'//span[contains(@id, "Instore")]/text()'
			),
			process=(
				lambda x: 'In Store' if
				x and 'visit one of our stores' in x.lower()
				else price_to_float(x)
			)
		),
		XGroup(
			name='price_gif',
			path=(
				'//div[contains(@class,"contentright")]/div/div[contains'
				'(@id, "AddToCart")]/a/img',
			)
		),
		XGroup(
			name='image',
			path=(
				'//div/img[contains(@id,"imgProduct")]/@src',
				'//div[@class="image"]/a/img/@src'
			),
		),
		XGroup(
			name='shipping',
			path=('//div/span[contains(@id, "Shipping")]/text()',)
		),
		XGroup(
			name='availability',
			default=True
		)
	)

	def get_breadcrumbs(self, response, return_format='string'):
		# FIXME: How will return_format be passed in from console ??
		if return_format.lower() == 'string':
			crumbs = response.xpath(self.CRUMB_TRAIL_LABEL_PATHS).extract()
			breadcrumbs = '/'.join([c.strip() for c in crumbs])

		else:
			# Return a serializable json object
			breadcrumbs = {}

			for crumb in response.xpath(self.CRUMB_TRAIL_PATHS).extract():
				href = crumb.xpath('./@href')
				label = crumb.xpath('./text()')

				if href and label:
					breadcrumbs[href.strip().replace('.', '')] = label.strip()

				# Add code to figure it out if only one exists

		return breadcrumbs

	def get_product_details(self, response):
		crumbs = self.get_breadcrumbs(response)
		loader = ItemLoader(item = VisionsProduct())

		loader.add_value('breadcrumbs', crumbs)
		loader.add_value('url', response.url)

		if isinstance(crumbs, basestring):
			loader.add_value('category', crumbs)

		# Ensure we aren't wasting time extracting from an empty page
		if extract_helper(response,self.EMPTY_PAGE_CHECK):
			for d in self.PRODUCT_DETAILS:
				if '_' not in d.name: # Don't load pric
					loader.add_value(d.name, 'N/A') # FIXME
		else:
			productDetails = detailsRunner(
				self.PRODUCT_DETAILS, response=response
			)

			if not productDetails['price']:
				productDetails['price'] = productDetails['price_gif']

			productDetails.pop('price_gif')

			# Fix truncated image urls
			if productDetails['image']:
				productDetails['image'] = add_schema(
					response.url, productDetails['image']
				)

			for d in productDetails:
				loader.add_value(d, productDetails[d])

		yield loader.load_item()

	def parse_product(self, response):
		all_links = [i for i in self.PRODUCT_PAGE_PATHS]
		all_links.extend([i for i in self.BUNDLE_PAGE_PATHS])

		product_links = extract_helper(response, all_links)

		if product_links:
			# Parse out urls ../../ refers to Catalogue/Category
			if 'bundle' not in response.url.lower():
				product_links = (
					'/Catalogue/Category/' + product_links if
					product_links.startswith('Details.aspx') else product_links
				)
			else:
				product_links = (
					'/Catalogue/Bundles/' + product_links if
					product_links.startswith('Details.aspx') else product_links
				)
			url = add_schema(
				response.url, re.sub('\.+/*\.+', '', product_links)
			)
			yield Request(url, callback=self.get_product_details)
		else:
			# We have landed on a product page, parse the product details
			yield self.get_product_details(response)

	def parse_category(self, response):
		'''
			Products are listed under a particular brand or subcategory.
			Use either to grab the product.
		'''
		# For debug, bundles and open box page not supported as the pages
		# have no breadcrumbs.
		crumbs = self.get_breadcrumbs(response)
		log.msg('IN ' + str(crumbs))

		if not extract_helper(response, self.EMPTY_PAGE_CHECK):
			yield Request(
				response.url, callback=self.parse_product, dont_filter=True
			)
		else:
			paths = [self.SUB_NAV_PATHS]
			paths.append(self.ALT_SUB_NAV_PATHS)
			subcat_link = extract_helper(response, paths)

			if subcat_link:
				subcat_link = re.sub(
					'Default.aspx',
					'/Catalogue/Category/ProductResults.aspx',
					subcat_link
				) if 'bundle' not in subcat_link.lower() else subcat_link

				url = add_schema(response.url, subcat_link)
				yield Request(url, callback=self.parse_category)

	def parse(self, response):
		for link in response.xpath(self.MAIN_NAV_PATHS).extract():
			url = add_schema(response.url, link)
			yield Request(url, callback=self.parse_category)

def main():
	VisionSpyder()

if __name__ == '__main__':
	main()