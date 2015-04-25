# Set up for Digital Ocean droplet to run this

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
    sudo apt-get install qgis python-qgis qgis-plugin-grass

6. Add to `~/.bashrc`:

    export PYTHONPATH=/usr/share/qgis/python/:$PYTHONPATH

7. SSH key setup

    ssh-keygen -t rsa -C "census-block-server"
    cat ~/.ssh/id_rsa.pub

    # Add as deploy key on Github
