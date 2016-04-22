from furl import furl
import re

def add_schema(parent_url, url):
	parent_url = furl(parent_url)
	url = furl(url)

	# Both urllib and furl can't parse out a host from urls like
	# www.google.ca. This is a quick workaround
	if not url.host and not url.url.lower().startswith('www'):
		url.host = parent_url.host

	url.scheme = url.scheme or parent_url.scheme

	# furl sometimes mistakes full urls for relative urls so on url.url
	# prepends that 'relative url' with a forward slash. Simple workaround.
	return re.sub(':///', '://', url.url)
