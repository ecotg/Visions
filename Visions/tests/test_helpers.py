import unittest
from Visions.utils import helpers

class TestHelpers(unittest.TestCase):
	def setUp(self):
		self.parent_url = (
			'http://www.visions.ca/Catalogue/Category/ProductResults.aspx'
		)

	def testUrl1(self):
		'''
			Test that helper adds in proper host and schema
		'''
		malformed_url = (
			'/Catalogue/Category/Details.aspx?categoryId=2'
		)
		self.assertEqual(
			helpers.add_schema(self.parent_url, malformed_url),
			'http://www.visions.ca/Catalogue/Category/Details.aspx?categoryId=2'
		)

	def testUrl2(self):
		'''
			Test that helper adds in only schema
		'''
		schemaless_url = 'www.visions.ca/Catalogue'

		self.assertEqual(
			helpers.add_schema(self.parent_url, schemaless_url),
			'http://www.visions.ca/Catalogue'
		)
