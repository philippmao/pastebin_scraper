#!usr/bin/python
import re, logging, peewee, time


"""
migrate pastes to a new table, which stores id, scrape_id (id of paste in scrape table, foreign key), contains, nr_of_results
pastes are moved if they contain IP address, mail address ...
if a paste contains multiple of these, multiple entries in the new table are created

CREATE TABLE Identifier (id INT NOT NULL AUTO_INCREMENT, scrape_id INT NOT NULL, category VARCHAR(255) NOT NULL, nr_of_results INT NOT NULL,
 PRIMARY KEY(id), FOREIGN KEY (scrape_id) REFERENCES Scrape(id));

"""

DB_HOST = "localhost"
DB_NAME = "scrapedb"
DB_USER = "scrape"
DB_PW = "scr@peo3d1e!"


logging.basicConfig(filename="db_migration_rules.log",
                            filemode='wb',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)

logger = logging.getLogger('Migration')



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


def init_identifier_model(db, Scrape):
    class Identifier(peewee.Model):
        scrape_id = peewee.ForeignKeyField(Scrape)
        category = peewee.CharField()
        nr_results = peewee.IntegerField()
        class Meta:
            database = db
    return Identifier


def identify(text):
    """
    check if text contains IP address, mail address ...
    :return: list of found identifiers
    """
    result = {}
    # check ip address
    ip = re.compile('(([2][5][0-5]\.)|([2][0-4][0-9]\.)|([0-1]?[0-9]?[0-9]\.)){3}'
                    + '(([2][5][0-5])|([2][0-4][0-9])|([0-1]?[0-9]?[0-9]))')
    matches = ip.finditer(text)
    c = 0
    for m in matches:
        c += 1
        print m.group()
    if c > 0:
        result["ip"] = c
    # check mail address
    mail = re.compile('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    matches = mail.finditer(text)
    c = 0
    for m in matches:
        c += 1
        print m.group()
    if c > 0:
        result["mail"] = c
    return result


def migrate_paste(id, raw, Identifier):
    ids = identify(raw)
    if "ip" in ids:
        ide = Identifier(scrape_id=id, category="ip", nr_of_results=ids["ip"])
        ide.save()
    if "mail" in ids:
        ide = Identifier(scrape_id=id, category="mail", nr_of_results=ids["mail"])
        ide.save()


def migrate_db(db, offset, Scrape, Identifier):
    query = Scrape.select(Scrape.id, Scrape.raw).offset(offset)
    cursor = db.execute(query)
    c = 0
    for (id, raw) in cursor:
        migrate_paste(id, raw, Identifier)
        c += 1
        if c % 5000 == 0:
            logging.info("offset at %s" % c)
    return c


def main():
    INITIAL_OFFSET = 0
    db = peewee.MySQLDatabase(DB_NAME, host=DB_HOST, user=DB_USER, passwd=DB_PW, charset='utf8')
    Scrape = init_scrape_model(db)
    Identifier = init_identifier_model(db, Scrape)
    off = migrate_db(db, INITIAL_OFFSET, Scrape, Identifier)
    while True:
        time.sleep(600)
        off = migrate_db(db, off, Scrape, Identifier)
        logging.info("finished migration up to offset: %s" %off)


if __name__ == "__main__":
    main()