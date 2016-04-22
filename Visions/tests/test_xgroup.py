import unittest
from Visions.utils.xgroup import (
	XGroup, price_to_float, extract_helper, detailsRunner,
)
from helpers import get_response

class TestdetailsRunner(unittest.TestCase):
	def testPage1(self):
		''' Test extracting data from a single xgroup '''

		url = (
			'http://www.visions.ca/Catalogue/Category/Details'
			'.aspx?categoryId=2&productId=29446&sku=KT609'
		)
		response = get_response('test_details_runner_page1', url=url)

		group = XGroup(
			name='title',
			path=(
				'//div[contains(@class, "contentright")]/h2/a/font/text()',
    			'div[contains(@class, "catalogueTitle")]/h3/text()',
    			'//h1/span[contains(@id, "ProdTitle")]/text()'
			),
			process=lambda x: x.upper()
		)

		detail = detailsRunner(group, response=response)
		self.assertEqual(
			detail['title'],
			'KT-609 3D-COMPATIBLE 1080P FULL HD ANDROID TV MEDIA BOX - '
			'HORIZONTAL BLACK'
		)

	def testPage2(self):
		''' Test extracting data from a list of xgroups '''
		url = (
			'http://www.visions.ca/Catalogue/Category/Details'
			'.aspx?categoryId=2&productId=29446&sku=KT609'
		)
		response = get_response('test_details_runner_page1', url=url)

		group = (
			XGroup(
				name='title',
				path=(
					'//div[contains(@class, "contentright")]/h2/a/font/text()',
	    			'div[contains(@class, "catalogueTitle")]/h3/text()',
	    			'//h1/span[contains(@id, "ProdTitle")]/text()'
				),
				process=lambda x: x.upper()
			),
			XGroup(
				name='shipping',
				path=('//div/span[contains(@id, "Shipping")]/text()'),
			),
			XGroup(
				name='availability',
				default=True
			)
		)

		detail = detailsRunner(group, response=response)
		self.assertEqual(
			detail['title'],
			'KT-609 3D-COMPATIBLE 1080P FULL HD ANDROID TV MEDIA BOX - '
			'HORIZONTAL BLACK'
		)
		self.assertEqual(detail['shipping'], 'Free Shipping!')
		self.assertTrue(detail['availability'])

class TestExtractHelper(unittest.TestCase):
	def testPage1(self):
		'''
			Test extraction using a single path and index==one
		'''
		url = (
			'http://www.visions.ca/catalogue/category/Details'
			'.aspx?categoryId=162&productId=4644&sku=KUBE2'
		)
		paths = ('//div/span[contains(@id, "Shipping")]/text()')
		response = get_response('test_extract_helper_page1', url=url)

		shipping = extract_helper(response, paths)

		self.assertEqual(shipping, 'Free Shipping!')

	def testPage2(self):
		'''
			Test extraction using a multiple paths and index==one
		'''
		url = (
			'http://www.visions.ca/catalogue/category/Details'
			'.aspx?categoryId=162&productId=4644&sku=KUBE2'
		)
		paths = (
			'//div/span[contains(@id, "price")]/a/text()'
			'//div/span[contains(@id, "price")]/text()',
			'//div[@class="productdetail-pricing"]/div/span[@id]/text()'
		)
		response = get_response('test_extract_helper_page1', url=url)

		price = extract_helper(response, paths)

		self.assertEqual(price, '$398.00')

	def testPage3(self):
		'''
			Test extraction using a multiple paths and index==all
		'''
		url = (
			'http://www.visions.ca/catalogue/category/Details'
			'.aspx?categoryId=162&productId=4644&sku=KUBE2'
		)

		paths = (
			'//div/span[contains(@id, "price")]/a/text()'
			'//div/span[contains(@id, "price")]/text()',
			'//div[@class="productdetail-pricing"]/div/span[@id]/text()'
		)

		response = get_response('test_extract_helper_page1', url=url)
		price = extract_helper(response, paths, index='all')

		self.assertEqual(price, ['$398.00', 'Save $502', '$899.99'])

class TestPrice2Float(unittest.TestCase):
	def testPrice1(self):
		''' Test price extraction '''
		self.assertEqual(price_to_float('sale: $2, 400'), 2400)
		self.assertEqual(price_to_float('$12.56'), 12.56)
		self.assertEqual(price_to_float(40), 40.0)
		self.assertIsNone(price_to_float('price'))
		self.assertIsNone(price_to_float([15.0, '25']))
		self.assertIsNone(price_to_float(''))