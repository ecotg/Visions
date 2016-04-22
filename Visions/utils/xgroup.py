import re
from collections import namedtuple
from scrapy import log

PRICE_RE = r'\$?(\d+[\.,]?\d+)' # 12.50 or $1,200

def price_to_float(price):
	if not isinstance(price, (basestring, float, int)):
		return None
	elif isinstance(price, (float,int)):
		return float(price)
	elif isinstance(price, basestring):
		price = re.sub(r'[\s\r\n]+', '', price)
		price = re.search(PRICE_RE, price)

		# replace commas to allow typecasting to float
		return float(price.group(1).replace(',','')) if price else None

def extract_helper(response, paths, index='one'):
	'''
		Extract elemets from a HTML page.
		@param: response Scrapy response object
		@params: paths String or Iterable of xpaths to use
    	@param: index Index of extracted result to use. Can be the one/first
    			extracted element or all extracted elements. (default: one)

    	@return: List or string of extracted element
	'''
	if not (response and paths):
		return

	index = index.lower()

	if isinstance(paths, basestring):
		data = response.xpath(paths).extract() or None
		return data[0] if data and index == 'one' else data

	elif isinstance(paths, (tuple, list)):
		data = []

		if index == 'one': # Fetch data of first element extract
			for p in paths:
				if not data:
					data = extract_helper(response, p, index=index)
				else:
					break
		else:
			for p in paths:
				result = (
					extract_helper(response, p, index=index) or []
				)
				data.extend(result)

		return data

def detailsRunner(xgroups, response=None):
	'''
	@param: XGroup. List of XGroups to extract product details. Type: Iterable
	@param: Scrapy response body used to find/extract elements.

	@return Dictionary of name: value of data extracted
	'''
	if not xgroups:
		return {}
	elif isinstance(xgroups, XGroup):
		xgroups = [xgroups]

	results = {}

	for group in xgroups:
		if response:
			group.response = response
		data = group.run()
		results[data.name] = data.value

	return results

class XGroup:
	def __init__(
		self,
		name='name',
		path=None,
		process=None,
		response=None,
		index='one',
		default=None
	):
		'''
			Extract and clean product details at the same time using the
			power of named tuples.

			@param: name Name of the detail being extracted
	    	@param: paths Xpaths to extract product details with. This can be
	    			String/List of Strings
	    	@param: process Process to clean/normalize extracted data. This can
	    			be None or a callable object (default None)
	    	@param: response Scrapy response object
	    	@param: index What index of extracted result to use. Can be the one/first
	    			extracted element or all extracted elements. (default: one)
	    	@param: default Default value. Use instead of extracting element. Type Bool

	    	@return Named tuple of extracted/cleaned data
		'''
		# FIXME. Raise exception if no response
		# Create namedtuple for input/output params
		self.xgroup = namedtuple(
			'xgroup', ['name', 'paths', 'process', 'response', 'index']
		)
		self.xvalue = namedtuple('xvalue', ['name', 'value'])

		self.paths = path
		self.process = process
		self.name = name
		self.response = response
		self.index = index
		self.default = default

	def extract(self):
		if self.default:
			self.extracted_data = self.default
		else:
			self.extracted_data = extract_helper(
				self.response, self.paths, self.index
			)

	def runProcess(self):
		''' Run the process on the extracted data '''
		if self.process and hasattr(self.process, '__call__'):
			self.processed_data = self.process(self.extracted_data)
		else:
			if self.name.endswith('price'):
				self.processed_data = price_to_float(self.extracted_data)
			else:
				self.processed_data = self.extracted_data

	def run(self):
		# extract
		self.extract()
		# run_process on data
		self.runProcess()
		# Initialize return tuple
		return self.xvalue(name=self.name, value=self.processed_data)
