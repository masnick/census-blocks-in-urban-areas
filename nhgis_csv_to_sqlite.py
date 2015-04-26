import pandas as pd
import sys # for sys.exit()
import os # for running shell commands
import code # for console breakpoint per http://stackoverflow.com/questions/8347636/drop-in-single-breakpoint-in-ruby-code
# code.interact(local=locals())

import sqlite3 as lite

import re # regexp

# Pretty printing for debugging
import pprint
pp = pprint.PrettyPrinter(indent=4)
# Usage: `pp.pprint(varname)`


if os.path.exists("data/nhgis/nhgis.db"):
  os.system('rm data/nhgis/nhgis.db')

con = lite.connect('data/nhgis/nhgis.db')

with con:
  cur = con.cursor()
  cur.execute("create table pop(state INT, county INT, tract INT, block INT, pop INT)")

  i = 0
  for line in open('data/nhgis/nhgis_ds172_2010_block.csv'):
    if i > 1:
      values = line.split(',')
      insert = tuple(int(float(re.subn(r'"', '', i)[0])) for i in (values[7], values[9], values[14], values[16], values[54]))
      sql = "insert into pop values(%s,%s,%s,%s,%s)" % insert
      # STATEA  7
      # COUNTYA 9
      # TRACTA  14
      # BLOCKA  16
      # H7V001  54
      cur.execute(sql)

      if i % 1000 == 0:
        print "Processing block %s..." % i

    i += 1

if con:
  con.close()
