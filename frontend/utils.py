#!/usr/bin/python
# coding: utf-8

import re, datetime, time
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from constants import DB_HOST, DB_NAME, DB_USER, DB_PW, DB_TABLE_NAME, SC_PER_PAGE

LEN_HIGHLIGHT = 30

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }


def add_to_where(where, condition):
  if len(where) > 0:
    where += " AND " + condition
  else:
    where += condition
  return where


def to_unix(date):
  """
  yyyy-mm-dd convert to unix timestamp (seconds since epoch)
  :param date:
  :return:
  """
  dt = re.compile('(([0-9])*)-([0-9][0-9])-([0-9][0-9])')
  mt = dt.match(date)
  t = datetime.datetime(int(mt.group(1)), int(mt.group(3)), int(mt.group(4)))
  # return timestamp with timezone conversion
  return time.mktime(t.timetuple())


def slider(mn, mx, max_r):
  while mn < 0:
    mn += 1
    if mx < max_r:
      mx +=1
  while mx > max_r:
    mx -= 1
    if mn > 0:
      mn -= 1
  return mn, mx


def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)


def add_mark(s, i1, i2):
  m1 = """<mark style="padding-right:0;padding-left:0">"""
  m2 = "</mark>"
  s = s[0:i1] + m1 + s[i1:i2] + m2 + s[i2:]
  return s


def add_highlight(s, i1, i2):
  if i1 < LEN_HIGHLIGHT:
    if len(s[i2:]) < 30:
      return add_mark(s, i1, i2)
    else:
      return add_mark(s[0:i2+30], i1, i2) + " ..."
  else:
    if len(s[i2:]) < 30:
      return "... " + add_mark(s[i1-30:], 30, i2-i1+30)
    else:
      return "... " + add_mark(s[i1-30:i2+30], 30, i2-i1+30) + " ..."


def find_highlight(s, search, identifier):
  if search == "":
    if identifier is None:
      return []
    else:
      if identifier == "ip":
        ip = re.compile('(([2][5][0-5]\.)|([2][0-4][0-9]\.)|([0-1]?[0-9]?[0-9]\.)){3}'
                        + '(([2][5][0-5])|([2][0-4][0-9])|([0-1]?[0-9]?[0-9]))')
        return ip.finditer(s)
      elif identifier == "mail":
        mail = re.compile('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        return mail.finditer(s)
      else:
        return []
  else:
    search = re.escape(search)
    return re.finditer(search.lower(), s.lower())


def highlight(s, search, identifier=None):
  r = find_highlight(s, search, identifier)
  rs = []
  for rr in r:
    rs.append(rr)
  if len(rs) == 0:
      return s[0:60], None
  is1, is2 = rs[0].start(), rs[0].end()
  ie1, ie2 = rs[-1].start(), rs[-1].end()
  rs1 = add_highlight(s, is1, is2)
  if ie1 == is1:
    rs2 = None
  else:
    rs2 = add_highlight(s, ie1, ie2)
  return rs1, rs2