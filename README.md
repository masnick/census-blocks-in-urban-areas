This repository is a set of scripts to find all the Census blocks in all the urban areas/urban clusters using 2010 data.

These scripts should run on Mac OS or on Ubuntu 14. See below for Ubuntu instructions.

- `find_blocks.py` will find the Census blocks that are geographically within each urban area/urban cluster
- `extract_populations_from_shapefiles.py` will pull out block-level population from shapefiles (because the Census doesn't make these data available in an easier way)


### Set up for Digital Ocean droplet to run `find_blocks.py` ###

1. New droplet using Ubuntu 14.04 x64
2. SSH in as root
3. Add to `/etc/apt/sources.list`:

    deb     http://qgis.org/debian trusty main
    deb-src http://qgis.org/debian trusty main

4. `sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 030561BEDD45F6C3` to fix error with key signing. You may also need to do this:

    gpg --keyserver keyserver.ubuntu.com --recv DD45F6C3
    gpg --export --armor DD45F6C3 | sudo apt-key add -

5. Run 

    sudo apt-get update
    sudo apt-get install qgis python-qgis qgis-plugin-grass git-core python-setuptools build-essential checkinstall python-pandas unzip

6. Add to `~/.bashrc`:

    export PYTHONPATH=/usr/share/qgis/python/:$PYTHONPATH

7. SSH key setup

    ssh-keygen -t rsa -C "census-block-server"
    cat ~/.ssh/id_rsa.pub

8. Add as deploy key on Github

9. Clone script

    git clone git@github.com:masnick/census-blocks-in-urban-areas.git ~/census

10. `shutdown -h now` and take snapshot

11. `tmux` and `cd census` and `python find_blocks.py workfiles/workerN.txt`

12. Spin up 4 other droplets using the snapshot, get to work!

13. When each worker is done, commit the output files to git and push.
