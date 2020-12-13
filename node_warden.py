import configparser
import logging
import os
import time
import pyttsx3

from logging.handlers import RotatingFileHandler

from connections import test_tor
from welcome import logo
from dashboard import main_dashboard

from ansi_management import (warning, success, error, info, clear_screen, bold,
                             muted)
from yaspin import yaspin

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
                        datefmt='%m/%d/%Y %I:%M:%S %p')


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


def greetings():
    # Welcome Sound
    if config['MAIN'].getboolean('welcome_sound'):
        with yaspin(text=config['MAIN'].get('welcome_text'),
                    color="cyan") as spinner:
            from yaspin.spinners import Spinners
            spinner.spinner = Spinners.moon
            engine = pyttsx3.init()
            engine.setProperty('rate', 270)
            engine.say(config['MAIN'].get('welcome_text'))
            engine.runAndWait()
            spinner.stop()
            spinner.write("")


if __name__ == '__main__':
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
    greetings()
    with yaspin(text="Launching Dashboard. Please Wait...",
                color="cyan") as spinner:
        main_dashboard(config, tor, spinner)
