#!/usr/bin/python
# coding: utf-8
import cgi, html, datetime
import mysql.connector as mariadb
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from constants import DB_HOST, DB_NAME, DB_USER, DB_PW, DB_TABLE_NAME, SC_PER_PAGE
from utils import highlight, html_escape
from page_generation import generate_normal_page, generate_navigation_buttons, generate_pagination, add_sorting_script


mariadb_connection = mariadb.connect(user=DB_USER, host=DB_HOST, password=DB_PW, database=DB_NAME)
cursor = mariadb_connection.cursor()

form = cgi.FieldStorage()


# Add buttons to navigate the search results
def add_bottom_part(search, offset, nr_results):
    html = generate_pagination(search, offset, nr_results)
    #html = generate_navigation_buttons(search, offset, nr_results)
    print html


def add_top_part(nr_results, offset, search):
    html = """<div class="container"><div class="row">"""
    if nr_results == 0:
        html += """<div class="col-sm-8"">
            <span class="border-success">   
            <h3>No Pastes found for "%s"</h3>
            </span>
            </div>""" % html_escape(search)
    else:
        html += """<div class="col-sm-8"">
        <span class="border-success">   
        <h3>%s Pastes found for "%s"</h3>
        </span>
        </div>
        """ % (nr_results, html_escape(search))
    html += """<div class="col-sm-4">
                <form class="form-search" action="/cgi-bin/rule_classification.py" >
                    <div class="input-group">
                    <input type="text" placeholder="Search.." name="search" class="form-control form-control">
                    <input type="hidden" name="search_offset" value=0>
                    <span class="input-group-btn-lg">
                        <button type="submit" class="btn btn-outline-success">Submit </button>
                    </span>
                    </div>
                </form>
            </div>"""
    html += """</div></div>"""
    print html


def do_search(search, offset, nr_results=None):
    # look through database return limit number of pastes, print them
    if search is None:
        search = ""
    bool_search = search
    if nr_results is None:
        cursor.execute("""SELECT COUNT(*) FROM identifier WHERE category=%(search)s""",
        {'search': bool_search})
        nr_results = cursor.fetchall()[0][0]
        print html_escape(cursor.statement)
    sql_offset = offset * SC_PER_PAGE
    cursor.execute("""SELECT * FROM identifier INNER JOIN scrape ON identifier.scrape_id = scrape.id WHERE category=%(search)s ORDER by scrape_id DESC LIMIT %(sql_offset)s, %(SC_PER_PAGE)s""",
                   {'search': bool_search, 'sql_offset': sql_offset, 'SC_PER_PAGE': SC_PER_PAGE})
    print html_escape(cursor.statement)
    result = cursor.fetchall()
    add_top_part(nr_results, offset, search)
    if nr_results == 0:
        return
    html = """<div class="container">"""
    html += """<table cellpadding="0" cellspacing="0" border="0" class="datatable table table-striped table-bordered" id="results">
    <thead>
    <tr>
        <th>Title</th>
        <th onclick="sortTableNumber(1)">Creation Date</th>
        <th> Raw Preview</th>
    </tr></thead>"""
    for (id1, scrape_id, category, nr_of_results, id2, scrape_url, full_url, date, paste_key, size, expire, title, syntax, raw) in result:
        if title == "":
            title = "Untitled"
        html += "<tr>\n"
        html += """<td> <a href="/cgi-bin/paste_inspection.py?id=%s" target="_blank">%s</a> </td>\n""" % (id2, title.encode('utf-8'))
        html += "<td data-ts=%s> %s </td>\n" % (int(date), datetime.datetime.fromtimestamp(int(date)).strftime('%d-%m-%Y %H:%M:%S'))
        raw1, raw2 = highlight(html_escape(raw.encode('utf-8')), "", identifier=search)
        if raw2 is not None:
            html += """<td> <p>%s</p> <p>%s</p> </td>\n""" % (raw1, raw2)
        else:
            html += """<td> <p>%s</p></td>\n""" % raw1
        html += "</tr>\n"
    html += "</table>\n"
    html += "</div>"
    print html
    add_bottom_part(search, offset, nr_results)
    print """<footer class="footer"> <div class="jumbotron text-center" style="margin-bottom:0">
      <p><a href="#h1">Up Top</a></p>
    </div> </footer>"""


try:
    offset = int(form.getvalue("search_offset"))
except:
    offset = 0
search = form.getvalue("search")
try:
    nr_results = int(form.getvalue("nr_results"))
except:
    nr_results = None


generate_normal_page()
add_sorting_script()
do_search(search, offset, nr_results=nr_results)
print """</body>
</html>"""


