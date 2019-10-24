#!/usr/bin/python
# coding: utf-8
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from constants import DB_HOST, DB_NAME, DB_USER, DB_PW, DB_TABLE_NAME, SC_PER_PAGE
from utils import slider


def generate_normal_page():
    print "Content-type: text/html\n\n"
    print """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Pastebin Scraper</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.0/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.0/js/bootstrap.min.js"></script>
</head>
<body>
    <div id="h1" class="b-4 p-2 page-header text-center" style="background-color: lightgrey;">
        <a href="/" style="text-decoration: none; color:#28a745">
            <h1>Pastebin Scraper</h1>
            <p>milCERT CTI project</p>
        </a>
    </div>

    <div class="container">
        <form class="pt-4 pb-3 form-search" action="/cgi-bin/pastebin.py" >
            <div class="row">
                <div class="col-xs-12 col-md-10">
                    <div class="input-group">
                        <input type="text" placeholder="Search.." name="search" class="form-control form-control">
                        <input type="hidden" name="search_offset" value=0>
                        <span class="input-group-btn-lg">
                            <button type="submit" class="btn btn-outline-success">Submit </button>
                        </span>
                    </div>
                </div>
                <div class="col-xs-12 col-md-2">
                    <button type="button" class="btn btn-link" data-toggle="collapse" data-target="#demo">Advanced</button>
                </div>
            </div>
            <div id="demo" class="mt-2 collapse">
                <ul class="nav nav-tabs">
                    <li class="nav-item active"><a class="nav-link active" data-toggle="tab" href="#home">Identifiers</a></li>
                    <li class="nav-item"><a class="nav-link" data-toggle="tab" href="#date">Date</a></li>
                    <li class="nav-item"><a class="nav-link" data-toggle="tab" href="#order">Order By</a></li>
                </ul>
                <div class="border-right border-left border-bottom">
                    <div class="tab-content">
                        <div id="home" class="p-3 tab-pane active">
                            <label class="radio-inline"><input type="radio" name="identifier" value="none" checked>None</label>
                            <label class="radio-inline"><input type="radio" name="identifier" value="ip" >Ip Addresses</label>
                            <label class="radio-inline"><input type="radio" name="identifier" value="mail">Mail Addresses</label>
                        </div>
                        <div id="date" class="p-3 tab-pane">
                            <label>Start: <input type="date" name="start"></label>
                            <label>End: <input type="date" name="end"></label>
                        </div>
                        <div id="order" class="p-3 tab-pane">
                            <label class="radio-inline"><input type="radio" name="order" value="new" checked>Newest</label>
                            <label class="radio-inline"><input type="radio" name="order" value="old" >Oldest</label>
                            <label class="radio-inline"><input type="radio" name="order" value="mrel">Most Relevant</label>
                            <label class="radio-inline"><input type="radio" name="order" value="lrel">Least Relevant</label>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </div>
"""


def generate_navigation_buttons(search, offset, nr_results):
    html = """<div class="container">
        <div style="margin-bottom:30px;">"""
    if offset == 0:
        if nr_results <= SC_PER_PAGE:
            # no button
            pass
        else:
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d" % (search, offset + 1, nr_results)
            # add next button
            html += """<a href="%s" class="btn btn-primary next">Next</a>""" % href

            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d" % (
            search, nr_results / SC_PER_PAGE, nr_results)
            # add next button
            html += """<a href="%s" class="btn btn-info btn-arrow-right">Last</a>""" % href
    else:
        if nr_results - offset * SC_PER_PAGE <= 50:
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=0&nr_results=%d" % (
                search, nr_results)
            # add next button
            html += """<a href="%s" class="btn btn-info btn-arrow-left">First</a>""" % href
            # prev button no next button
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d" % (search, offset - 1, nr_results)
            # add next button
            html += """<a href="%s" class="btn btn-primary previous">Previous</a>""" % href
        else:
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=0&nr_results=%d" % (
                search, nr_results)
            # add next button
            html += """<a href="%s" class="btn btn-info btn-arrow-left">First</a>""" % href
            html += """<div class="btn-group">"""
            # both buttons
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d" % (search, offset - 1, nr_results)
            # add next button
            html += """<a href="%s" class="btn btn-primary previous">Previous</a>""" % href
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d" % (search, offset + 1, nr_results)
            # add next button
            html += """<a href="%s" class="btn btn-primary next">Next</a>""" % href
            html += """</div>"""
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d" % (
                search, nr_results / SC_PER_PAGE, nr_results)
            # add next button
            html += """<a href="%s" class="btn btn-info btn-arrow-right">Last</a>""" % href
    html += """</div></div>"""
    return html


def generate_pagination(search, offset, nr_results, identifier, start, end, order):
    if identifier is None:
        identifier = "none"
    if start is None:
        start = ""
    if end is None:
        end = ""
    html = """<div class="container">
            <ul class="pagination">"""
    if nr_results % SC_PER_PAGE == 0:
        max_pages = nr_results / SC_PER_PAGE
    else:
        max_pages = nr_results/SC_PER_PAGE + 1
    if offset == 0:
        if nr_results <= SC_PER_PAGE:
            # no button
            pass
        else:
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                search, offset, nr_results, identifier, start, end, order)
            html += """<li class="page-item disabled"><a class="page-link" href="%s">%s</a></li>""" % (href, offset + 1)
            c = 1
            while c < 5 and c <= max_pages-1:
                of = offset + c
                href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                search, of, nr_results, identifier, start, end, order)
                html += """<li class="page-item"><a class="page-link" href="%s">%s</a></li>""" % (href, of+1)
                c += 1
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                search, offset + 1, nr_results, identifier, start, end, order)
            html += """<li class="page-item"><a class="page-link" href="%s">%s</a></li>""" % (href, ">")
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                search, max_pages-1, nr_results, identifier, start, end, order)
            html += """<li class="page-item"><a class="page-link" href="%s">%s</a></li>""" % (href, ">>")
    else:
        if nr_results - offset * SC_PER_PAGE <= 50:
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                search, 0, nr_results, identifier, start, end, order)
            html += """<li class="page-item"><a class="page-link" href="%s">%s</a></li>""" % (href, "<<")
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                search, offset-1, nr_results, identifier, start, end, order)
            html += """<li class="page-item"><a class="page-link" href="%s">%s</a></li>""" % (href, "<")
            c = min(offset, 4)
            while c > 0:
                of = offset - c
                href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                    search, of, nr_results, identifier, start, end, order)
                html += """<li class="page-item"><a class="page-link" href="%s">%s</a></li>""" % (href, of + 1)
                c -= 1
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                search, offset, nr_results, identifier, start, end, order)
            html += """<li class="page-item disabled"><a class="page-link" href="%s">%s</a></li>""" % (href, offset + 1)
        else:
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                search, 0, nr_results, identifier, start, end, order)
            html += """<li class="page-item"><a class="page-link" href="%s">%s</a></li>""" % (href, "<<")
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                search, offset - 1, nr_results, identifier, start, end, order)
            html += """<li class="page-item"><a class="page-link" href="%s">%s</a></li>""" % (href, "<")

            mn, mx = slider(offset-2, offset+2, max_pages-1)

            for of in range(mn, mx+1):
                if of == offset:
                    href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                        search, offset, nr_results, identifier, start, end, order)
                    html += """<li class="page-item disabled"><a class="page-link" href="%s">%s</a></li>""" % (
                    href, offset + 1)
                else:
                    href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                        search, of, nr_results, identifier, start, end, order)
                    html += """<li class="page-item"><a class="page-link" href="%s">%s</a></li>""" % (href, of + 1)

            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                search, offset + 1, nr_results, identifier, start, end, order)
            html += """<li class="page-item"><a class="page-link" href="%s">%s</a></li>""" % (href, ">")
            href = "/cgi-bin/pastebin.py?search=%s&search_offset=%d&nr_results=%d&identifier=%s&start=%s&end=%s&order=%s" % (
                search, max_pages - 1, nr_results, identifier, start, end, order)
            html += """<li class="page-item"><a class="page-link" href="%s">%s</a></li>""" % (href, ">>")
    html += """</ul></div>"""
    return html


def add_sorting_script():
    print """<script>
function sortTableNumber(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("results");
  switching = true;
  //Set the sorting direction to ascending:
  dir = "asc"; 
  /*Make a loop that will continue until
  no switching has been done:*/
  while (switching) {
    //start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /*Loop through all table rows (except the
    first, which contains table headers):*/
    for (i = 1; i < (rows.length - 1); i++) {
      //start by saying there should be no switching:
      shouldSwitch = false;
      /*Get the two elements you want to compare,
      one from current row and one from the next:*/
      x = rows[i].getElementsByTagName("TD")[n].getAttribute("data-ts");
      y = rows[i + 1].getElementsByTagName("TD")[n].getAttribute("data-ts");
      /*check if the two rows should switch place,
      based on the direction, asc or desc:*/
      if (dir == "asc") {
        if (x > y) {
          //if so, mark as a switch and break the loop:
          shouldSwitch= true;
          break;
        }
      } else if (dir == "desc") {
        if (x < y) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /*If a switch has been marked, make the switch
      and mark that a switch has been done:*/
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      //Each time a switch is done, increase this count by 1:
      switchcount ++;      
    } else {
      /*If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again.*/
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
</script>"""

    print """<script>
function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("results");
  switching = true;
  //Set the sorting direction to ascending:
  dir = "asc"; 
  /*Make a loop that will continue until
  no switching has been done:*/
  while (switching) {
    //start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /*Loop through all table rows (except the
    first, which contains table headers):*/
    for (i = 1; i < (rows.length - 1); i++) {
      //start by saying there should be no switching:
      shouldSwitch = false;
      /*Get the two elements you want to compare,
      one from current row and one from the next:*/
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /*check if the two rows should switch place,
      based on the direction, asc or desc:*/
      if (dir == "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          //if so, mark as a switch and break the loop:
          shouldSwitch= true;
          break;
        }
      } else if (dir == "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /*If a switch has been marked, make the switch
      and mark that a switch has been done:*/
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      //Each time a switch is done, increase this count by 1:
      switchcount ++;      
    } else {
      /*If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again.*/
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
</script>"""