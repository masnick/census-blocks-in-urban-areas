from qgis.core import *
# Note: add /Applications/QGIS.app/Contents/Resources/python/ to the PYTHONPATH environment variable for this to import.

import pandas as pd
import sys # for sys.exit()
import os # for running shell commands
import code # for console breakpoint per http://stackoverflow.com/questions/8347636/drop-in-single-breakpoint-in-ruby-code
# code.interact(local=locals())

# Pretty printing for debugging
import pprint
pp = pprint.PrettyPrinter(indent=4)
# Usage: `pp.pprint(varname)`

# supply path to where is your qgis installed
if sys.platform == "darwin":
  QgsApplication.setPrefixPath("/Applications/QGIS.app/Contents/MacOS", True)
elif sys.platform == "linux2":
  QgsApplication.setPrefixPath("/usr", True)

QgsApplication.initQgis()


# Valid state numerical codes
# From https://www.census.gov/geo/reference/ansi_statetables.html
valid_states = [1, 2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56]

# Set up output dataframe
columns = ['state', 'county', 'tract', 'block', 'block_id', 'pop10', 'housing10']
output_df = pd.DataFrame(columns=columns)

for st in valid_states:

  # Get filename
  filename = "tabblock2010_%02d_pophu" % st

  # Check to see if shapefile has been downloaded
  # If not, download it
  if not os.path.exists("data/census/block_population/%s/%s.shp" % (filename, filename)):
    cmd = "cd data/census/block_population && rm -rf %s && mkdir %s && cd %s && curl -O ftp://ftp2.census.gov/geo/tiger/TIGER2010BLKPOPHU/%s.zip && unzip %s.zip" % (filename, filename, filename, filename, filename)
    os.system(cmd)

  # Load shapefile for this state
  blocks_in_state_layer = QgsVectorLayer("data/census/block_population/%s/%s.shp" % (filename, filename), "blocks", "ogr")
  if not blocks_in_state_layer.isValid():
    print "Layer %s failed to load!" % st

  # Extract attributes
  field_names = [field.name() for field in blocks_in_state_layer.pendingFields() ]

  for block in blocks_in_state_layer.getFeatures():
    block_attributes =  dict(zip(field_names, block.attributes()))
    data = [{
      'state': block_attributes['STATEFP10'],
      'county': block_attributes['COUNTYFP10'],
      'tract': block_attributes['TRACTCE10'],
      'block': block_attributes['BLOCKCE'],
      'block_id': block_attributes['BLOCKID10'],
      'pop10': block_attributes['POP10'],
      'housing10': block_attributes['HOUSING10']
    }]
    output_df = output_df.append(data)

output_df.to_csv("data/census/output/block_population.csv", index = False)

# cleanup
QgsApplication.exitQgis()
