API_ADDRESS = lambda x: 'https://yande.re/post.json?limit=100&page=%d' % x
API_ADDRESS_2 = lambda y: 'https://konachan.com/post.json?limit=%s' % y
PROXY_ADDRESS = 'http://127.0.0.1:1081'
MAX_RETRIES = 5
CACHE_DIR = './cache'
DISABLE_RANK = 'EQ'
MAX_SEND = 3