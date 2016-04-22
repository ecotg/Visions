import unittest
from helpers import get_response
from Visions.spiders import VisionSpider

class TestVisionscom(unittest.TestCase):
	def setUp(self):
		self.spider = VisionSpider()

	def testMainNav(self):
		'''
			Test extraction from the front/main page
		'''
		url = 'http://www.visions.ca/Default.aspx'
		response = get_response('front_page', url=url)
		subcategories = list(self.spider.parse(response))

		self.assertEqual(len(subcategories), 14)
		self.assertEqual(
			subcategories[0].url,
			'http://www.visions.ca/Catalogue/Category/'
			'Default.aspx?categoryId=2&menu=2'
		)
		self.assertEqual(
			subcategories[-1].url,
			'http://www.visions.ca/Catalogue/Bundles/Default.aspx'
		)

	def testSubCategories(self):
		'''
			Test that spider extracts link to one subcategory
		'''
		url = (
			'http://www.visions.ca/Catalogue/Category/Default.aspx'
			'?categoryId=368&menu=7'
		)

		response = get_response('subcat_page', url=url)
		subcategories = list(self.spider.parse_category(response))

		self.assertEqual(len(subcategories), 1)
		self.assertEqual(
			subcategories[0].url,
			'http://www.visions.ca/Catalogue/Category/Product'
			'Results.aspx?categoryId=144&view='
		)

	def testProductLinks(self):
		'''
			Test spider extracts link to product page
		'''
		url = (
			'http://www.visions.ca/Catalogue/Category/Product'
			'Results.aspx?categoryId=94&view='
		)

		response = get_response('product_page', url=url)
		products = list(self.spider.parse_product(response))

		self.assertEqual(len(products), 1)
		self.assertEqual(
			products[0].url,
			'http://www.visions.ca/Catalogue/Category/Details.'
			'aspx?categoryId=94&productId=8027&sku=CR2360'
		)

	def testProductLinks2(self):
		'''
			Test spider extracts link to product page - bundles page
		'''
		url = 'http://www.visions.ca/Catalogue/Bundles/Default.aspx'

		response = get_response('product_page2', url=url)
		products = list(self.spider.parse_product(response))

		self.assertEqual(len(products), 1)
		self.assertEqual(
			products[0].url,
			'http://www.visions.ca/Catalogue/Bundles/Details.'
			'aspx?bundleId=2838'
		)

	def testProductDetails(self):
		'''
			Test spider extracts product details
		'''
		url = (
			'http://www.visions.ca/Catalogue/Category/Details.'
			'aspx?categoryId=498&productId=10168&sku=AGF310'
		)
		response = get_response('page1', url=url)
		details = self.spider.get_product_details(response).next()

		self.assertEqual(
			details,
			{
				'availability': True,
 				'breadcrumbs': 'Home/TV & Video/3D TV Glasses',
 				'category': 'Home/TV & Video/3D TV Glasses',
 				'image': (
 					'http://www.visions.ca/Images/Catalogue/Product'
 					'/English/AGF310_l_1.jpg'
 				),
 				'price': 9.99,
 				'product': 'LG Cinema 3D Glasses - Single Pair',
 				'url': url
 			}
		)
