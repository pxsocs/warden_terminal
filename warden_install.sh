#!/bin/bash

helpFunction()
{
    echo ""
    echo "\tWARden Run Script"
    echo "\t-------------------------------------------------------------------------------------"
    echo "\tUsage: $0 --parameters"
    echo ""
    echo "\tParameters:"
    echo "\t --help\t\t\tDisplays this help"
    echo "\t --install\t\t\tInstalls the WARden at startup"
    echo "\t --upgrade\t\t\tUpgrade to latest version"
    echo ""
    exit 1 # Exit script after printing help
}

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
python3 node_warden
}

python_params=()
# Get Arguments from shell script
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -h|--help)
    HELP=true
    shift # past argument
    ;;
    -s|--setup)
    SETUP=true
    shift # past argument
    ;;
    -u|--upgrade)
    UPGRADE=true
    shift # past argument
    ;;

    *)    # unknown option - pass to python
    python_params+=("$1")
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

if [ "$HELP" = true ] ; then
    helpFunction
fi

if [ "$SETUP" = true ] ; then
    # Check if Python3 is installed
    command -v python3 2>&1 || pythonNotFound
    # install package requirements
    installPackages
    runApp
fi

if [ "$UPGRADE" = true ] ; then
    # Get new git
    echo Upgrading from GitHub:
    git fetch --all
    git reset --hard origin/master
    # install package requirements
    echo Installing Python Package Requirements
    installPackages
    echo Done
    runApp
fi

