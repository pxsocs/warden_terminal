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
                             muted, yellow, blue)

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
                print(yellow("Upgrading from GitHub: ")),
                import subprocess
                subprocess.run("git fetch --all", shell=True)
                subprocess.run("git reset --hard origin/master", shell=True)
                print(yellow("Installing Python Package Requirements")),
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
                if config['MAIN'].getboolean('sound'):
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 270)
                    engine.say(config['MAIN'].get('welcome_text'))
                    engine.runAndWait()
            except Exception:
                pass
            spinner.stop()
            spinner.write("")


def check_cryptocompare():
    with yaspin(text=f"Testing price grab from Cryptocompare",
                color="green") as spinner:
        config = load_config(True)
        api_key = config['API'].get('cryptocompare')
        # tickers should be in comma sep string format like "BTC,ETH,LTC" and "USD,EUR"
        baseURL = (
            "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC" +
            "&tsyms=USD&api_key=" + api_key)
        try:
            request = tor_request(baseURL)
        except requests.exceptions.ConnectionError:
            spinner.fail("💥 ")
            spinner.write(
                warning("    Connection Error - check internet connection"))
            exit()

        data = request.json()

        try:
            if data['Response'] == 'Error':
                config_file = os.path.join(basedir, 'config.ini')
                spinner.fail("💥 ")
                spinner.write(warning("    CryptoCompare Returned an error"))
                print("    " + data['Message'])
                if data['Message'] == 'You are over your rate limit please upgrade your account!':
                    # First try to get a random API KEY
                    if config['API'].getboolean('random') is not True:
                        print(
                            "    Looks like you are over the API Limit. Will try to generate a random API."
                        )
                        size = 16
                        import binascii
                        random_key = binascii.b2a_hex(os.urandom(size))
                        config['API']['random'] = 'True'
                        config['API']['cryptocompare'] = str(
                            random_key.decode("utf-8"))
                        with open(config_file, 'w') as configfile:
                            config.write(configfile)
                        check_cryptocompare()
                        return

                    print(
                        '    -----------------------------------------------------------------'
                    )
                    print(
                        yellow("    Looks like you need to get an API Key. "))
                    print(
                        yellow("    The WARden comes with a shared key that"))
                    print(yellow("    eventually gets to the call limit."))
                    print(
                        '    -----------------------------------------------------------------'
                    )
                    print(
                        blue(
                            '    Go to: https://www.cryptocompare.com/cryptopian/api-keys'
                        ))
                    print(muted("    Current API:"))
                    print(f"    {api_key}")
                    new_key = input('    Enter new API key (Q to quit): ')
                    if new_key == 'Q' or new_key == 'q':
                        exit()
                    config['API']['cryptocompare'] = new_key
                    with open(config_file, 'w') as configfile:
                        config.write(configfile)
                    check_cryptocompare()
        except KeyError:
            try:
                btc_price = (data['DISPLAY']['BTC']['USD']['PRICE'])
                spinner.ok("✅ ")
                spinner.write(success(f"    BTC price is: {btc_price}"))
                return
            except Exception:
                spinner.fail("💥 ")
                spinner.write(
                    warning("    CryptoCompare Returned an UNKNOWN error"))
                print(data)

        return (data)


def exception_handler(exctype, value, tb):
    os.execv(sys.executable, ['python3'] + [sys.argv[0]] + ['quiet'])
    # print(exctype)
    # print(tb.print_last())


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
        check_cryptocompare()
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
    print(success("   Launching the Dashboard..."))
    main_dashboard(config, tor)
