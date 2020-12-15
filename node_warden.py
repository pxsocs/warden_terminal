import configparser
import logging
import os
import sys
import subprocess
# Upon the first import of non standard libraries, if not found
# Start pip install
try:
    import pyttsx3
    import requests
    from yaspin import yaspin
except ModuleNotFoundError:
    subprocess.run("pip3 install -r requirements.txt", shell=True)

from logging.handlers import RotatingFileHandler

from connections import test_tor, tor_request
from welcome import logo
from dashboard import main_dashboard

from ansi_management import (warning, success, error, info, clear_screen, bold,
                             muted, yellow)

# Main Variables
basedir = os.path.abspath(os.path.dirname(__file__))
debug_file = os.path.join(basedir, 'debug.log')


def load_config(quiet=False):
    # Load Config
    config_file = os.path.join(basedir, 'config.ini')
    CONFIG = configparser.ConfigParser()
    if quiet:
        CONFIG.read(config_file)
        return (CONFIG)

    with yaspin(text="Loading config.ini", color="cyan") as spinner:

        # Check that config file exists
        if os.path.isfile(config_file):
            CONFIG.read(config_file)
            spinner.ok("✅ ")
            spinner.write(success("    Config Loaded [Success]"))
            print("")
            return (CONFIG)
        else:
            spinner.fail("💥 ")
            spinner.write(
                warning("    Config file could not be loaded [ERROR]"))
            print(error("    WARden requires config.ini to run. Quitting..."))
            exit()


def launch_logger():
    # Config of Logging
    formatter = "[%(asctime)s] %(message)s"
    logging.basicConfig(handlers=[
        RotatingFileHandler(filename=debug_file,
                            mode='w',
                            maxBytes=120,
                            backupCount=0)
    ],
                        level=logging.INFO,
                        format=formatter,
                        datefmt='%I:%M:%S %p')


def create_tor():
    # ----------------------------------------------
    #                 Test Tor
    # ----------------------------------------------
    with yaspin(text="Testing Tor", color="cyan") as spinner:
        tor = test_tor()
        if tor['status']:
            logging.info(success("Tor Connected"))
            spinner.ok("✅ ")
            spinner.write(success("    Tor Connected [Success]"))
            print("")
            return (tor)
        else:
            logging.error(error("Could not connect to Tor"))
            spinner.fail("💥 ")
            spinner.write(warning("    Tor NOT connected [ERROR]"))
            print(
                error(
                    "    Could not connect to Tor. WARden requires Tor to run. Quitting..."
                ))
            print(
                info(
                    "    Download Tor at: https://www.torproject.org/download/"
                ))
            print("")
            exit()


def check_version():
    from dashboard import version
    current_version = version()
    with yaspin(
            text=f"Checking for updates. Running version: {current_version}",
            color="green") as spinner:

        url = 'https://raw.githubusercontent.com/pxsocs/warden_terminal/master/version.txt'
        try:
            remote_version = tor_request(url).text
        except Exception:
            print(yellow("  [!] Could not reach GitHub to check for upgrades"))
            return

        if str(remote_version).strip() == str(current_version).strip():
            spinner.ok("✅ ")
            spinner.write(success("    You are running latest version"))
        else:
            spinner.fail("💥 ")
            spinner.write(
                warning(f"    Update available - version: {remote_version}"))
            import click
            if click.confirm(warning('    [?] Would you like to upgrade?'),
                             default=False):
                print(" ---------------------------------------")
                print(yellow(f"Upgrading from GitHub: ")),
                import subprocess
                subprocess.run("git fetch --all", shell=True)
                subprocess.run("git reset --hard origin/master", shell=True)
                print(yellow(f"Installing Python Package Requirements")),
                subprocess.run("pip3 install -r requirements.txt", shell=True)
                print(" ---------------------------------------")
                print(success("  ✅ Done Upgrading"))

        print("")


def greetings():
    # Welcome Sound
    if config['MAIN'].getboolean('welcome_sound'):
        with yaspin(text=config['MAIN'].get('welcome_text'),
                    color="cyan") as spinner:
            from yaspin.spinners import Spinners
            spinner.spinner = Spinners.moon
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 270)
                engine.say(config['MAIN'].get('welcome_text'))
                engine.runAndWait()
            except Exception:
                pass
            spinner.stop()
            spinner.write("")


def exception_handler(exctype, value, tb):
    os.execv(sys.executable, ['python3'] + [sys.argv[0]] + ['quiet'])


if __name__ == '__main__':
    if 'quiet' not in sys.argv:
        clear_screen()
        logo()
        print("")
        try:
            os.remove(debug_file)
        except Exception:
            pass
        launch_logger()
        logging.info(muted("Starting main program..."))
        config = load_config()
        tor = create_tor()
        check_version()
        greetings()
    else:
        launch_logger()
        config = load_config(True)
        tor = {
            "pre_proxy": 'Restarting...',
            "post_proxy": 'Restarting...',
            "post_proxy_ping": 'Restarting...',
            "pre_proxy_ping": 'Restarting...',
            "difference": 'Restarting...',
            "status": True,
            "port": 'Restarting...'
        }
    sys.excepthook = exception_handler
    main_dashboard(config, tor)
