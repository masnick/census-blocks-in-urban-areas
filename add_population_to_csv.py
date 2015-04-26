import pandas as pd
import numpy as np
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


con = lite.connect('data/nhgis/nhgis.db')

with con:
  cur = con.cursor()

  # Get all the output CSV files
  path = 'data/census/output'
  onlyfiles = [ f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) and re.match(r'.*csv$',f)]

  for file in onlyfiles:
    # Read in CSV file for editing
    csv = pd.read_csv(os.path.join(path,file), quotechar='"')

    # Add column for population
    csv['pop'] = -1

    # Loop through rows
    for i,row in enumerate(csv.iterrows()):
      sql = "select pop from pop where state = %d and county = %d and tract = %d and block = %d" % (row[1]['state'], row[1]['county'], row[1]['tract'], row[1]['block'])
      cur.execute(sql)
      rows = cur.fetchall()

      if len(rows) != 1:
        raise Exception('There are %s rows for %s' % (len(rows), sql))

      csv.set_value(i, 'pop', rows[0][0])

    csv.to_csv("data/census/output_with_population/%s" % file, index = False)

if con:
  con.close()
