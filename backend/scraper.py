#!usr/bin/python

import requests, MySQLdb, peewee, time, json, logging, sys, collections


"""Insert your own mysql information"""
DB_HOST = ""
DB_NAME = ""
DB_USER = ""
DB_PW = ""
DB_TABLE_NAME = "scrape"
# times 60 seconds for general duplicate removal
GENERAL_CLEANUP_COUNTER = 60
# size of duplicate check FIFO queue
FIFO_SIZE = 1000

# CREATE THE DATABASE
"""CREATE TABLE scrape (id INT NOT NULL AUTO_INCREMENT, scrape_url VARCHAR(255) NOT NULL, full_url VARCHAR(255) NOT NULL, date VARCHAR(255) NOT NULL, paste_key VARCHAR(255) NOT NULL, size VARCHAR(255) NOT NULL, expire VARCHAR(255) NOT NULL, title TEXT NOT NULL, syntax VARCHAR(255) NOT NULL, raw TEXT NOT NULL, PRIMARY KEY ( id ), FULLTEXT(raw) COMMENT 'parser "TokenBigramSplitSymbolAlpha"')
#   ENGINE=Mroonga; """


def init_scrape_model(db):
	class Scrape(peewee.Model):
		scrape_url = peewee.CharField()
		full_url = peewee.CharField()
		date = peewee.CharField()
		paste_key = peewee.CharField()
		size = peewee.CharField()
		expire = peewee.CharField()
		title = peewee.TextField()
		syntax = peewee.CharField()
		user = peewee.CharField
		raw = peewee.TextField()
		class Meta:
			database = db
	return Scrape


logging.basicConfig(filename="paste_bin_scraper.log",
                            filemode='wb',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)

logger = logging.getLogger('Scraper')


def get_scrapes(Scrape, queue):
	try:	
		last_n_posts = requests.get('https://scrape.pastebin.com/api_scraping.php?limit=100').text
	except:
		logging.exception("error retrievieng scrape info!")
		return
	try:	
		json_posts = json.loads(last_n_posts)
	except:
		logging.exception("error decoding json!")
		logging.exception(last_n_posts)
		return
	for post in json_posts:
		duplicate_found = False
		paste_key = post["key"]
		try:
			if paste_key in queue:
				queue.remove(paste_key)
				queue.appendleft(paste_key)
				duplicate_found = True
			else:
				queue.appendleft(paste_key)
		except:
			logging.exception("error managing fifo queue!")
		try:
			raw = requests.get('https://scrape.pastebin.com/api_scrape_item.php?i=%s' % paste_key).text
		except:
			logging.exception("error retrieving raw scrape!")			
			continue 
		#print raw, post
		scrape_to_db(post, raw, Scrape, duplicate_found)


def scrape_to_db(post, raw_text, Scrape, duplicate_found):
	raw_text = raw_text.encode('utf-8')
	if duplicate_found:
		sc = Scrape.update(raw=raw_text).where(Scrape.paste_key == post["key"])
		sc.execute()
	else:
		sc = Scrape(scrape_url = post["scrape_url"], full_url = post["full_url"], date = post["date"], paste_key = post["key"], size = post["size"],\
				expire = post["expire"], title = post["title"].encode('utf-8'), syntax = post["syntax"], user = post["user"], raw = raw_text)
		sc.save()


def rm_dup(db):
	try:
		db.execute_sql("DELETE t1 FROM scrape t1 INNER JOIN scrape t2 WHERE t1.id < t2.id AND t1.paste_key = t2.paste_key;")
	except:
		logging.exception("error removing duplicates")


def scraping_program():
	# connect to DB
	db = peewee.MySQLDatabase(DB_NAME, host=DB_HOST, user=DB_USER, passwd=DB_PW, charset='utf8')
	Scrape = init_scrape_model(db)
	Scrape.create_table()
	fifo_queue = collections.deque([], FIFO_SIZE)
	while True:
		get_scrapes(Scrape, fifo_queue)
		time.sleep(60)


if __name__=="__main__":
	sys.stdout = open('peewee_logs.txt', 'w')
	try:
		scraping_program()
	except:
		logging.exception("uncaught error! :/")
