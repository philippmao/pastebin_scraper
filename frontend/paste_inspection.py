#!/usr/bin/python
# coding: utf-8
import cgi, html, datetime
import mysql.connector as mariadb
from utils import html_escape
from constants import DB_HOST, DB_NAME, DB_USER, DB_PW, DB_TABLE_NAME, SC_PER_PAGE
from page_generation import generate_normal_page

mariadb_connection = mariadb.connect(user=DB_USER, host=DB_HOST, password=DB_PW, database=DB_NAME)
cursor = mariadb_connection.cursor()

form = cgi.FieldStorage()


def display_paste(id):
    cursor.execute("SELECT * FROM scrape WHERE id=%(pid)s", {'pid': id})
    id, scrape_url, full_url, date, paste_key, size, expire, title, syntax, raw = cursor.fetchall()[0]
    if title == "":
        title = "Untitled"
    if expire == "0":
        expire = "never"
    else:
        expire = datetime.datetime.fromtimestamp(int(expire)).strftime('%d-%m-%Y %H:%M:%S')
    print """<div class="container">
    <div class="p-2 row">
        <div class="col">Title: %s</div>
        <div class="col">Date: %s</div>
        <div class="col">Syntax: %s</div>
        <div class="col">Expire: %s</div>
        <div class="col">URL: %s</div>
  </div>""" %(title.encode('utf-8'), datetime.datetime.fromtimestamp(int(date)).strftime('%d-%m-%Y %H:%M:%S'),
                      syntax.encode('utf-8'), expire.encode('utf-8'), full_url.encode('utf-8'))
    print """<div class="row">
    <textarea style="width:100%%; height:400px">%s</textarea></div>""" % html_escape(raw.encode('utf-8'))

generate_normal_page()

id = int(form.getvalue("id"))

display_paste(id)

print """</body>
</html>"""


