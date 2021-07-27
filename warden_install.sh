#!/bin/bash


pythonNotFound()
{
    echo ""
    echo "\tPython3 does not seem to be installed in this machine"
    echo "\tplease install to use WARden. Download and instructions:"
    echo "\thttps://www.python.org/"
    echo ""
    exit 1
}

installPackages()
{
    python3 -m pip install -r requirements.txt
}

runApp()
{
# Launch app
# Check for Python 3
command -v python3 2>&1 || pythonNotFound
python3 node_warden.py
}


command -v python3 2>&1 || pythonNotFound

echo "\tThis script will install "
