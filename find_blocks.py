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


# Unzip urban area shapefile if needed
if not os.path.exists("data/census/urban_areas/tl_2010_us_uac10.shp"):
  print "Unzipping urban area shapefile"
  cmd = "cd data/census/urban_areas && unzip tl_2010_us_uac10.zip"
  os.system(cmd)

# Load in list of urban areas for processing
with open (sys.argv[1], "r") as myfile:
  to_process = [int(float(i)) for i in myfile.readlines()]

# supply path to where is your qgis installed
if sys.platform == "darwin":
  QgsApplication.setPrefixPath("/Applications/QGIS.app/Contents/MacOS", True)
else if sys.platform == "linux2":
  QgsApplication.setPrefixPath("/usr", True)

# load providers
QgsApplication.initQgis()

# If you have trouble loading layers, see this: http://gis.stackexchange.com/questions/59069/creating-qgis-layers-in-python-console-vs-stand-alone-application

urban_areas_layer = QgsVectorLayer("data/census/urban_areas/tl_2010_us_uac10.shp", "urban_areas", "ogr")
if not urban_areas_layer.isValid():
  print "Layer failed to load!"



# Valid state numerical codes
# From https://www.census.gov/geo/reference/ansi_statetables.html
valid_states = [1, 2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56]

# Relationships between urban areas and counties
# http://www2.census.gov/geo/docs/maps-data/data/rel/ua_county_rel_10.txt
urban_areas_counties = pd.read_csv('data/census/urban_areas/urban_area_county.txt', quotechar='"')


# Gets the names of the fields in a layer
# http://gis.stackexchange.com/questions/76364/how-to-get-field-names-in-pyqgis-2-0
field_names = [field.name() for field in urban_areas_layer.pendingFields() ]


for urban_area in urban_areas_layer.getFeatures():
  block_count = 0
  attributes =  dict(zip(field_names, urban_area.attributes()))

  # Check to see if this urban area should be processed by this instance
  if int(float(attributes['UACE10'])) not in to_process:
    print "\n\nSkipping %s" % attributes['UACE10']
    continue

  print "\n\nStarting urban area %s..." % attributes['NAME10']

  # Set up output dataframe
  columns = ['ua_name', 'ua_id', 'state', 'county', 'tract', 'block', 'block_geoid']
  output_df = pd.DataFrame(columns=columns)


  # Look up counties that this UA covers
  counties = urban_areas_counties[(urban_areas_counties.UA == int(float(attributes['UACE10'])))]

  # Skip any counties that aren't in the US
  counties = counties[counties['STATE'].isin(valid_states)]

  # Check to see if shapefiles are already downloaded
  for county in counties.iterrows():
    print "    Starting county %s" % county[1]['CNAME']

    # Figure out filename for shapefile for county
    zero_pad_state = '%02d' % int(float(county[1]['STATE']))
    zero_pad_county = '%03d' % int(float(county[1]['COUNTY']))
    filename = 'tl_2010_%s%s_tabblock10' % (zero_pad_state, zero_pad_county)

    # Download shapefile for county if it hasn't been downloaded already
    if not os.path.exists("data/census/blocks/%s/%s.shp" % (filename, filename)):
      cmd = "cd data/census/blocks && rm -rf %s && mkdir %s && cd %s && curl -O ftp://ftp2.census.gov//geo/tiger/TIGER2010/TABBLOCK/2010/%s.zip && unzip %s.zip" % (filename, filename, filename, filename, filename)
      os.system(cmd)

    # Load in block layer for county
    block_layer = QgsVectorLayer("data/census/blocks/%s/%s.shp" % (filename, filename), "blocks", "ogr")
    if not block_layer.isValid():
      print "Layer %s.shp to load!" % filename
    else:
      # Get field names for block
      field_names_blocks = [field.name() for field in block_layer.pendingFields() ]

      for block in block_layer.getFeatures():
        if block.geometry().within(urban_area.geometry()) == True:
          block_attributes =  dict(zip(field_names_blocks, block.attributes()))
          block_count += 1
          # print "        Block found: %s" % block_attributes['GEOID10']

          # Need to dump the following attributes:
          #   STATEFP10
          #   COUNTYFP10
          #   TRACTCE10
          #   BLOCKCE10
          #   GEOID10
          #
          # Along with this, save the urban area info:
          #   attributes['NAME10']
          #   attributes['UACE10']
          #
          # columns = ['ua_name', 'ua_id', 'state', 'county', 'tract', 'block', 'block_geoid']

          data = [{
            'ua_name': attributes['NAME10'],
            'ua_id': attributes['UACE10'],
            'state': block_attributes['STATEFP10'],
            'county': block_attributes['COUNTYFP10'],
            'tract': block_attributes['TRACTCE10'],
            'block': block_attributes['BLOCKCE10'],
            'block_geoid': block_attributes['GEOID10']
          }]
          output_df = output_df.append(data)


          # code.interact(local=locals())
          # sys.exit()
  print "%d block(s) found for %s" % (block_count, attributes['NAME10'])

  output_df.to_csv("data/census/output/%s.csv" % attributes['UACE10'], index = False)

# cleanup
QgsApplication.exitQgis()
