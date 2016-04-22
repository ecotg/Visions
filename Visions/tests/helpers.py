from scrapy.http import HtmlResponse
import inspect

TEST_DATA_DIR = 'data'

def call_stack():
	stack = inspect.stack()
	filepath = stack[2][1]
	module = filepath.split('/')[:-1]
	module = '/'.join(module)

	return module

def get_response(file_name, url='', ext='html'):
	response = None
	module = call_stack()
	ext = '.' + ext if '.' not in ext else ext

	try:
		file_dir = module + '/' + TEST_DATA_DIR + '/'
		_file_ = file_dir + file_name + ext

		with open(_file_, 'r') as infile:
			contents = infile.read()
			if contents:
				response = HtmlResponse(url=url, body=contents)
	except IOError, e:
		print e

	return response