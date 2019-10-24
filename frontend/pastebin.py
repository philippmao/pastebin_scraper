#!/usr/bin/python
# coding: utf-8
import cgi, html, datetime
import mysql.connector as mariadb
from constants import DB_HOST, DB_NAME, DB_USER, DB_PW, DB_TABLE_NAME, SC_PER_PAGE
from utils import highlight, html_escape, to_unix, add_to_where
from page_generation import generate_normal_page, generate_navigation_buttons, generate_pagination, add_sorting_script


mariadb_connection = mariadb.connect(user=DB_USER, host=DB_HOST, password=DB_PW, database=DB_NAME)
cursor = mariadb_connection.cursor()

form = cgi.FieldStorage()


# Add buttons to navigate the search results
def add_bottom_part(search, offset, nr_results, start, end, order_input):
    html = generate_pagination(search, offset, nr_results, identifier, start, end, order_input)
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
    print html


def time_constraint(start, end):
    if start is None and end is None:
        return None
    elif start is None and end is not None:
        return "date <= %(end)s"
    elif start is not None and end is None:
        return "date >= %(start)s"
    else:
        return "date <= %(end)s AND date >= %(start)s"


def get_order(id, order):
    if order == "new":
        return "date DESC"
    elif order == "old":
        return "date"
    else:
        #TODO: implement relevance
        return "%s DESC" % id


def do_search(search, identifier, offset, start, end, order_input, nr_results=None):
    # look through database return limit number of pastes, print them
    if identifier == "none":
        identifier = None
    if start is None:
        start_time = None
    else:
        start_time = to_unix(start)
    if end is None:
        end_time = None
    else:
        end_time = to_unix(end)
    if search is None:
        search = ""
    where = ""
    limit = "%(sql_offset)s, %(SC_PER_PAGE)s"
    if identifier is not None:
        table = "identifier INNER JOIN scrape ON identifier.scrape_id = scrape.id"
        select = "scrape_id, scrape_url, full_url, date, paste_key, size, expire, title, syntax, raw"
        order = get_order("scrape_id", order_input)
        where = add_to_where(where, "category=%(identifier)s")
    else:
        table = "scrape"
        order = get_order("id", order_input)
        select = "*"
    bool_search = "(\"" + search + "\")"
    if identifier is None:
        where = add_to_where(where, "MATCH(raw) AGAINST(%(search)s IN BOOLEAN MODE)")
    else:
        if search != "":
            where = add_to_where(where, "MATCH(raw) AGAINST(%(search)s IN BOOLEAN MODE)")
    tc = time_constraint(start_time, end_time)
    if tc is not None:
        where = add_to_where(where, tc)
    if nr_results is None:
        query = """SELECT COUNT(*) FROM %s WHERE %s""" % (table, where)
        cursor.execute(query,
        {'identifier': identifier, 'search': bool_search, 'start': start_time, 'end': end_time})
        nr_results = cursor.fetchall()[0][0]
    sql_offset = offset * SC_PER_PAGE
    query = """SELECT %s FROM %s WHERE %s ORDER by %s LIMIT %s""" % (select, table, where, order, limit)
    cursor.execute(query, {'identifier': identifier, 'search': bool_search, 'start': start_time, 'end': end_time, 'sql_offset': sql_offset, 'SC_PER_PAGE': SC_PER_PAGE})
    result = cursor.fetchall()
    add_top_part(nr_results, offset, search)
    if nr_results == 0:
        return
    html = """<div class="container">"""
    html += """<table cellpadding="0" cellspacing="0" border="0" class="datatable table table-striped table-bordered" id="results">
    <thead>
    <tr>
        <th>Title</th>
        <th>Creation Date</th>
        <th> Raw Preview</th>
    </tr></thead>"""
    for (id, scrape_url, full_url, date, paste_key, size, expire, title, syntax, raw) in result:
        if title == "":
            title = "Untitled"
        html += "<tr>\n"
        html += """<td> <a href="/cgi-bin/paste_inspection.py?id=%s" target="_blank">%s</a> </td>\n""" % (id, title.encode('utf-8'))
        html += "<td data-ts=%s> %s </td>\n" % (int(date), datetime.datetime.fromtimestamp(int(date)).strftime('%d-%m-%Y %H:%M:%S'))
        raw1, raw2 = highlight(html_escape(raw.encode('utf-8')), html_escape(search), identifier=identifier)
        if raw2 is not None:
            html += """<td> <p>%s</p> <p>%s</p> </td>\n""" % (raw1, raw2)
        else:
            html += """<td> <p>%s</p></td>\n""" % raw1
        html += "</tr>\n"
    html += "</table>\n"
    html += "</div> </div> </div>"
    print html
    add_bottom_part(search, offset, nr_results, start, end, order_input)
    print """<div class="footer"> <div class="jumbotron text-center" style="margin-bottom:0">
      <p><a href="#h1">Up Top</a></p>
    </div>"""


try:
    offset = int(form.getvalue("search_offset"))
except:
    offset = 0
search = form.getvalue("search")
identifier = form.getvalue("identifier")
start = form.getvalue("start")
end = form.getvalue("end")
order = form.getvalue("order")
try:
    nr_results = int(form.getvalue("nr_results"))
except:
    nr_results = None


generate_normal_page()
add_sorting_script()
do_search(search, identifier, offset, start, end, order, nr_results=nr_results)
print """</body>
</html>"""


