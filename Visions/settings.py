# -*- coding: utf-8 -*-

# Scrapy settings for Visions project
from datetime import datetime
import os

BOT_NAME = 'Visions'

SPIDER_MODULES = ['Visions.spiders']
NEWSPIDER_MODULE = 'Visions.spiders'

LOG_ENABLED = True
LOG_ENCODING = 'utf-8'
timestamp = datetime.now().strftime('%Y-%b-%d:%I-%M-%p')
LOG_FILE = str(os.getcwd() + '/Visions' + '/LOGS/' + BOT_NAME + '-' + timestamp + '.log')

# Export results, as a json feed, to file
FEED_DIR = '/'.join(os.getcwd().split('/')[:-1]) + '/spiders/FEEDS'
FEED_URI = 'file:///' + FEED_DIR + '/%(name)s' + '/' + timestamp + '.json'
FEED_FORMAT = 'json'

FEED_EXPORTERS = {
     'json': 'scrapy.contrib.exporter.JsonItemExporter',
}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Visions (+http://www.yourdomain.com)'
