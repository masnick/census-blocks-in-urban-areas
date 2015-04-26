This repository is a set of scripts to find all the Census blocks in all the urban areas/urban clusters using 2010 data.

__The [output of these scripts is available](https://github.com/masnick/census-blocks-in-urban-areas/releases) so you don't have to run them yourself.__ If you do want to run them for some reason, see below.

### Running these scripts

These scripts should run on Mac OS or on Ubuntu 14. See below for Ubuntu setup instructions.

1. Get the the list of Census blocks in each urban area/urban cluster
    - `find_blocks.py` will find the Census blocks that are geographically within each urban area/urban cluster using the shapefiles.
        - __Input:__
            - A list of which counties each urban area/urban cluster overlaps in `data/census/urban_areas/urban_area_county.txt` (provided in this repo)
            - A shapefile for all the urban areas in the US in `data/census/urban_areas/tl_2010_us_uac10.shp` (automatically unzipped by the script; zip in repo)
            - The shapefiles for each county, downloaded automatically by this script into `data/census/blocks` as needed.
        - __Output:__ CSV files for each urban area are saved in `data/census/output`.
    - It turns out that the county shapefiles actually have the urban area each block belongs to in them. So this could be optimized to use this rather than the spatial query.

2. Get the population for each of the blocks in an urban area/urban cluster
    - Unfortunately, the county shapefiles don't include the population for each block. There are two sources for this information: (1) state shapefiles including each block or (2) query from the excellent [NHGIS Data Finder](https://www.nhgis.org/).
    - `extract_populations_from_shapefiles.py` will pull out block-level population from state shapefiles, but is too slow to use in practice.
        -  `population_shapefile_downloader.py` will let you download the shapefiles for every state in parallel.
    - The NHGIS query takes a long time to run as well, so I have made the output (csv) [available here](https://dl.dropboxusercontent.com/u/634/permanent/census-blocks-in-urban-areas/nhgis0001_csv.zip).
        - The extracted CSV file is >2gb, so it is necessary to convert it into a database using `nhgis_csv_to_sqlite.py`. Again, you can save some time by using the output of this script (tar.gz of an sqlite3 database) [available here](https://dl.dropboxusercontent.com/u/634/permanent/census-blocks-in-urban-areas/nhgis.db.tar.gz).
    - `add_population_to_csv.py` uses the sqlite database to add a `pop` column to all the CSV files in `data/census/output/`. It saves new CSV files in `data/census/output_with_population`. It expects the sqlite database to be at `data/nhgis/nhgis.db`. __See below about how to optimize performance for the DB -- if you don't do this, this script will be incredibly slow.__

3. Combine individual urban area CSV files into one single CSV file (`combine_csvs.rb`). This will output `data/census/blocks_with_population.csv`. This file is [available to download here](https://github.com/masnick/census-blocks-in-urban-areas/releases).


#### Ubuntu set-up for Digital Ocean droplet to run `find_blocks.py` ###

1. New droplet using Ubuntu 14.04 x64
2. SSH in as root
3. Add to `/etc/apt/sources.list`:

        deb     http://qgis.org/debian trusty main
        deb-src http://qgis.org/debian trusty main

4. `apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 030561BEDD45F6C3` to fix error with key signing.

5. Run 

        apt-get update
        apt-get install qgis python-qgis qgis-plugin-grass git-core python-setuptools build-essential checkinstall python-pandas unzip

6. Add to `~/.bashrc`:

        export PYTHONPATH=/usr/share/qgis/python/:$PYTHONPATH

7. SSH key setup

        ssh-keygen -t rsa -C "census-block-server"
        cat ~/.ssh/id_rsa.pub

8. Add as deploy key on Github

9. Clone script

        git clone git@github.com:masnick/census-blocks-in-urban-areas.git ~/census

10. `shutdown -h now` and take snapshot so you can spin up 4 more to do this in parallel

11. SSH back in as root to each server, run `tmux` and `cd census` and `python find_blocks.py workfiles/workerN.txt`

12. When each worker is done, commit the output files to git and push.


#### Optimizing sqlite3 database for NHGIS data

The NHGIS data are >2gb unzipped, so we need to use a database to query them rather than loading the CSV into memory. We will use sqlite3 for this.

At the command line, run `sqlite3 data/nhgis/nhgis.db` once you have created the database using `nhgis_csv_to_sqlite.py`.

Then run this:

    explain query plan select pop from pop where state = 1 and county = 1 and tract = 20100 and block = 1000;

This will indicate that sqlite has to `SCAN` the table (slow) rather than using an index.

Run this to create an index:

    create index poplookup on pop (state, county, tract, block);

This will take a few minutes. Once it finishes running, run the query plan explainer again. You should get this:

    SEARCH TABLE pop USING INDEX poplookup (state=? AND county=? AND tract=? AND block=?)
