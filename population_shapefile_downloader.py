import sys # for sys.exit()
import os # for running shell commands
import code # for console breakpoint per http://stackoverflow.com/questions/8347636/drop-in-single-breakpoint-in-ruby-code
# code.interact(local=locals())

# Pretty printing for debugging
import pprint
pp = pprint.PrettyPrinter(indent=4)


if sys.argv[1] == "1":
  valid_states = [1, 2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22]
elif sys.argv[1] == "2":
  valid_states = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
elif sys.argv[1] == "3":
  valid_states = [37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56]
else:
  print "arg error"


for st in valid_states:
  filename = "tabblock2010_%02d_pophu" % st
  if not os.path.exists("data/census/block_population/%s/%s.shp" % (filename, filename)):
    cmd = "cd data/census/block_population && rm -rf %s && mkdir %s && cd %s && curl -O ftp://ftp2.census.gov/geo/tiger/TIGER2010BLKPOPHU/%s.zip && unzip %s.zip" % (filename, filename, filename, filename, filename)
    os.system(cmd)
