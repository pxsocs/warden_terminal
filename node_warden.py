# Upon the first import of non standard libraries, if not found
from pathlib import Path
from pickle import load
import pyttsx3
import requests
from yaspin import yaspin

import configparser
import subprocess
from data import (data_btc_rpc_info, data_large_block, data_logger, data_login,
                  data_mempool, data_random_satoshi, data_sys, data_tor,
                  data_btc_price, data_specter)
import logging
import os
import sys

import json
from random import randrange
from apscheduler.schedulers.background import BackgroundScheduler

from logging.handlers import RotatingFileHandler

from connections import test_tor, tor_request
from welcome import logo, goodbye
from dashboard import main_dashboard

from ansi_management import (warning, success, error, info, clear_screen,
                             muted, yellow, blue)

basedir = os.path.abspath(os.path.dirname(__file__))
debug_file = os.path.join(basedir, 'debug.log')
# Check if critical paths exist
Path(basedir + '/static/save').mkdir(parents=True, exist_ok=True)
# Sometimes the log path below does not exist and is needed
try:
    Path('/var/log/wtmp').mkdir(parents=True, exist_ok=True)
except Exception:
    pass


def load_config(quiet=False):
    # Load Config
    basedir = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.join(basedir, 'config.ini')
    CONFIG = configparser.ConfigParser()
    if quiet:
        CONFIG.read(config_file)
        return (CONFIG)

    print("")
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
    try:
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
        logging.getLogger('apscheduler').setLevel(logging.CRITICAL)

    except Exception:
        pass


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


def check_version(upgrade_args=True):
    from dashboard import version
    current_version = version()
    logging.info(f"Running WARden version: {current_version}")
    pickle_it('save', 'restart.pkl', False)
    with yaspin(
            text=f"Checking for updates. Running version: {current_version}",
            color="green") as spinner:

        url = 'https://raw.githubusercontent.com/pxsocs/warden_terminal/master/version.txt'
        try:
            remote_version = tor_request(url).text
        except Exception:
            print(yellow("  [!] Could not reach GitHub to check for upgrades"))
            return

        upgrade = False

        try:
            from packaging import version as packaging_version
            parsed_github = packaging_version.parse(remote_version)
            parsed_version = packaging_version.parse(current_version)
            if parsed_github > parsed_version:
                upgrade = True

        except Exception:
            if str(remote_version).strip() != str(current_version).strip():
                upgrade = True

        if not upgrade:
            spinner.ok("✅ ")
            spinner.write(success("    You are running the latest version"))

        if upgrade:
            spinner.fail("[i] ")
            spinner.write(
                warning(f"    Update available - version: {remote_version}"))

            print(f"    [i] You are running version: {current_version}")

            if (upgrade_args is True):
                import click
                if click.confirm(warning('    [?] Would you like to upgrade?'),
                                 default=False):
                    print(" ---------------------------------------")
                    print(yellow("Upgrading from GitHub: ")),
                    import subprocess
                    subprocess.run("git fetch --all", shell=True)
                    subprocess.run("git reset --hard origin/master",
                                   shell=True)
                    print(yellow("Installing Python Package Requirements")),
                    subprocess.run("pip3 install -r requirements.txt",
                                   shell=True)
                    print(" ---------------------------------------")
                    print(success("  ✅ Done Upgrading"))
                    print(success("     RESTARTING...."))
                    upgrade = False
                    pickle_it('save', 'restart.pkl', True)
                    # Try to restart the app
                    try:
                        os.execl(sys.executable, os.path.abspath(__file__),
                                 *sys.argv)
                    except Exception:
                        pass

            else:
                logging.info(
                    error(
                        "An Upgrade is available for the WARden. Run the app with the --upgrade argument to update to the latest version."
                    ))
                print(
                    error(
                        "    [i] run the app with --upgrade argument to upgrade"
                    ))

        print("")
        pickle_it('save', 'upgrade.pkl', upgrade)


def greetings():
    # Clean saved price
    pickle_it('save', 'multi_price.pkl', 'loading...')
    pickle_it('load', 'last_price_refresh.pkl', 0)
    config = load_config()
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
    with yaspin(text="Testing price grab from Cryptocompare",
                color="green") as spinner:
        data = {'Response': 'Error', 'Message': None}
        try:
            api_key = pickle_it('load', 'cryptocompare_api.pkl')
            if api_key != 'file not found':
                baseURL = (
                    "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC"
                    + "&tsyms=USD&api_key=" + api_key)
                request = tor_request(baseURL)
                data = request.json()
                data = request.json()
                btc_price = (data['DISPLAY']['BTC']['USD']['PRICE'])
                spinner.text = (success(f"BTC price is: {btc_price}"))
                spinner.ok("✅ ")
                pickle_it('save', 'cryptocompare_api.pkl', api_key)
                return
            else:
                data = {'Response': 'Error', 'Message': 'No API Key is set'}
        except Exception as e:
            data = {'Response': 'Error', 'Message': str(e)}

        try:
            if data['Response'] == 'Error':
                spinner.color = 'yellow'
                spinner.text = "CryptoCompare Returned an error " + data[
                    'Message']

                # ++++++++++++++++++++++++++
                #  Load Legacy
                # ++++++++++++++++++++++++++
                try:
                    # Let's try to use one of the
                    # legacy api keys stored under cryptocompare_api.keys file
                    # You can add as many as you'd like there
                    filename = 'cryptocompare_api.keys'
                    file = open(filename, 'r')
                    for line in file:
                        legacy_key = str(line)

                        spinner.text = (
                            warning(f"Trying different API Keys..."))

                        baseURL = (
                            "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC"
                            + "&tsyms=USD&api_key=" + legacy_key)

                        try:
                            request = tor_request(baseURL)
                            data = request.json()
                            btc_price = (
                                data['DISPLAY']['BTC']['USD']['PRICE'])
                            spinner.text = (
                                success(f"BTC price is: {btc_price}"))
                            spinner.ok("✅ ")
                            pickle_it('save', 'cryptocompare_api.pkl',
                                      legacy_key)
                            return
                        except Exception:
                            spinner.text = "Didn't work... Trying another."

                except Exception:
                    pass

                spinner.text = (error("Failed to get API Key - read below."))
                spinner.fail("[!]")

                print(
                    '    -----------------------------------------------------------------'
                )
                print(yellow("    Looks like you need to get an API Key. "))
                print(yellow("    The WARden comes with a shared key that"))
                print(yellow("    eventually gets to the call limit."))
                print(
                    '    -----------------------------------------------------------------'
                )
                print(
                    yellow(
                        '    Go to: https://www.cryptocompare.com/cryptopian/api-keys'
                    ))
                print(
                    yellow(
                        '    To get an API Key. Keys from cryptocompare are free.'
                    ))
                print(
                    yellow(
                        '    [Tip] Get a disposable email to signup and protect privacy.'
                    ))
                print(
                    yellow(
                        '    Services like https://temp-mail.org/en/ work well.'
                    ))

                print(muted("    Current API:"))
                print(f"    {api_key}")
                new_key = input('    Enter new API key (Q to quit): ')
                if new_key == 'Q' or new_key == 'q':
                    exit()
                pickle_it('save', 'cryptocompare_api.pkl', new_key)
                check_cryptocompare()
        except KeyError:
            try:
                btc_price = (data['DISPLAY']['BTC']['USD']['PRICE'])
                spinner.ok("✅ ")
                spinner.write(success(f"BTC price is: {btc_price}"))
                pickle_it('save', 'cryptocompare_api.pkl', api_key)
                return
            except Exception:
                spinner.text = (
                    warning("CryptoCompare Returned an UNKNOWN error"))
                spinner.fail("💥 ")

        return (data)


def login_tip():
    from pricing_engine import current_path
    filename = os.path.join(current_path(), 'static/json_files/tips.json')
    with open(filename) as tips_json:
        tips = json.load(tips_json)["did_you_know"]
    tip = tips[randrange(len(tips))]
    logging.info(tip)
    instructions = {
        "[H]": "Show / Hide Private Info",
        "[Arrows]": "Scroll Through Screens",
        "[S]": "Auto Scroll On / Off",
        "[M]": "Force Multi Widgets (large screens)",
        "[D]": "Download Bitcoin Whitepaper",
        "[A]": "Audio On / Off",
        "[!]": "Restart the App",
        "[Q]": "Quit the app"
    }
    string = '----------\n              Keyboard Commands:\n'
    for key, val in instructions.items():
        string += '              ' + key + ' ' + val + '\n'
    logging.info(string)
    logging.info(success("Like the app? Donate:"))
    logging.info(
        success("tipping.me (Lightning): https://tippin.me/@alphaazeta"))
    logging.info(
        success(
            "onchain bc1q4fmyksw40vktte9n6822e0aua04uhmlez34vw5gv72zlcmrkz46qlu7aem"
        ))


def check_screen_size():
    with yaspin(text=f" Checking terminal screen size",
                color="green") as spinner:
        rows, columns = subprocess.check_output(['stty', 'size']).split()
        rows = int(rows)
        columns = int(columns)
        xs_display = False
        small_display = False
        # min dimensions are recommended at 60 x 172
        if rows < 60 or columns < 172:
            small_display = True
            config = load_config(quiet=True)
            config_file = os.path.join(basedir, 'config.ini')
            # When starting, always enable auto scroll through widgets
            # the refresh variable on config.ini determines how many seconds
            # to wait between refreshes
            config['MAIN']['auto_scroll'] = 'True'
            if columns < 50 or rows < 20:
                xs_display = True
                config['MAIN']['large_text_font'] = 'small'
            with open(config_file, 'w') as configfile:
                config.write(configfile)

        cycle = int(0)
        pickle_it('save', 'cycle.pkl', cycle)
        message = f"Screen size is {str(rows)} rows x {str(columns)} columns"
        spinner.text = (success(message))
        spinner.ok("✅ ")

        logging.info(message)
        pickle_it('save', 'xs_display.pkl', xs_display)
        pickle_it('save', 'small_display.pkl', small_display)
        pickle_it('save', 'multi_toggle.pkl', False)
        if small_display:
            print(
                yellow(
                    "    [i] Small display detected.\n        Will cycle through widgets.\n        Pressing (M) on main screen will force multi gadget display."
                ))
            logging.info(
                'Small Screen Detected. Cycling through screens. [S] to toggle.'
            )
        print("")


def check_btc_rpc():
    #  Check if Bitcoin's RPC is available. See rpc.py for defaults and environment vars.
    print("")
    rpc_running = False
    pickle_it('save', 'rpc_running.pkl', rpc_running)

    with yaspin(text="Checking if Bitcoin RPC is reachable",
                color="green") as spinner:
        from rpc import rpc_connect
        rpc = rpc_connect()
        if rpc is None:
            spinner.fail("[i] ")
            spinner.write(warning("     Bitcoin RPC unreachable"))
        else:
            try:
                bci = rpc.getblockchaininfo()
                chain = bci['chain']
                pickle_it('save', 'rpc_running.pkl', True)
                spinner.ok("✅ ")
                spinner.write(success(f"    RPC reached: Chain {chain}"))
                logging.info("[Bitcoin Core] RPC is available")
            except Exception as e:
                spinner.fail("[i] ")
                spinner.write(
                    warning(f"    Bitcoin RPC returned an error: {e}"))
                logging.warning(
                    warning("Could not reach Bitcoin RPC. Check config.ini."))


def clean_url(url, port=None):
    if url[-1] == '/':
        url = url[:-1]
    if 'http' not in url:
        url = 'http://' + url
    if port is None:
        url = f'{url}/'
    else:
        url = f'{url}:{port}/'
    return (url)


def check_nodetype():
    # Checks which node is running and save urls to different apps
    raspiblitz_detected = pickle_it('load', 'raspiblitz_detected.pkl')
    umbrel_detected = pickle_it('load', 'umbrel.pkl')
    mynode_detected = pickle_it('load', 'mynode_detected.pkl')
    local_ip = pickle_it('load', 'ip.pkl')
    node = None
    config = load_config(quiet=True)
    # CHECK RASPIBLITZ --------------------
    try:
        if raspiblitz_detected is True:
            # Adjust IP addreses and URLs
            if local_ip is not None:
                try:
                    specter_port = config['SPECTER']['specter_port']
                except Exception:
                    specter_port = '25441'
                specter_ip = clean_url(local_ip, specter_port)
                pickle_it('save', 'specter_ip.pkl', specter_ip)
            node = "raspiblitz"
    except Exception:
        pass

    # CHECK UMBREL ------------------------
    try:
        if umbrel_detected is True:
            try:
                specter_port = config['SPECTER']['specter_port']
            except Exception:
                specter_port = '25441'
            if config['UMBREL']['url'] != 'None':
                specter_ip = config['UMBREL']['url']
            specter_ip = clean_url(specter_ip, specter_port)
            pickle_it('save', 'specter_ip.pkl', specter_ip)
            node = "umbrel"
    except Exception:
        pass

    # CHECK MyNode ------------------------
    try:
        if mynode_detected is True:
            node = "mynode"
    except Exception:
        pass

    if node is None:
        logging.warning(
            "[WARN] Could not autodetect a Bitcoin Node running. Check config.ini."
        )
    else:
        logging.info(f"[INFO] Autodetected node: {node}")

    return node


def check_mynode():
    mynode_detected = False
    print("")
    config = load_config(quiet=True)
    with yaspin(text="Checking if running MyNode ⚡", color="green") as spinner:
        try:
            # Check if the path /var/www/mynode exists
            mynode_detected = Path('/var/www/mynode').is_dir()
            if mynode_detected is True:
                spinner.write(
                    success("    MyNode node detected in this machine."))
                logging.info("[MyNode] Running inside MyNode")

                # Now we can get the bitcoin RPC data
                d = {}
                d['rpc_user'] = 'mynode'
                try:
                    with open("/mnt/hdd/mynode/settings/.btcrpc_environment",
                              "r") as f:
                        for line in f:
                            if "=" in line:
                                key, val = map(str.strip, line.split("="))
                                d[key] = val
                                if 'PASSWORD' in line:
                                    d['rpc_password'] = val
                except Exception:
                    d['rpc_password'] = "error_getting_password"

                d['rpc_port'] = 8332
                d['rpc_ip'] = '127.0.0.1'

                # Save this for later
                pickle_it('save', 'mynode_bitcoin.pkl', d)

            else:
                raise Exception("MyNode not detected")

        except Exception:
            mynode_detected = False

        # May not be running inside mynode but let's check if a MyNode
        # is present in local network.
        try:
            url = config['MYNODE'].get('url')
        except Exception:
            url = 'http://mynode.local/'

        # Test if this url can be reached
        try:
            result = tor_request(url)
            if not isinstance(result, requests.models.Response):
                raise Exception(f'Did not get a return from {url}')
            if not result.ok:
                raise Exception(f'Reached {url} but an error occured.')
            mynode_detected = True
            spinner.ok("✅ ")
            spinner.write(success(f"    MyNode found on {url}"))

        except Exception as e:
            spinner.fail("[i] ")
            spinner.write(
                warning(
                    f"     MyNode node not detected and not reachable. Error {e}"
                ))
            mynode_detected = False

        pickle_it('save', 'mynode_detected.pkl', mynode_detected)


def check_raspiblitz():

    # We can also check if running inside a raspiblitz and get
    # additional node and bitcoin.conf info.
    raspiblitz_detected = False
    print("")
    with yaspin(text="Checking if running inside Raspiblitz Node ⚡",
                color="green") as spinner:
        try:
            raspi_file = '/home/admin/raspiblitz.info'
            # Check if exists
            if not os.path.isfile(raspi_file):
                raise FileNotFoundError
            raspiblitz_detected = True
            # Save data to dictionary
            filename = open(raspi_file, "r")
            d = {}
            for line in filename:
                if "=" in line:
                    key, val = map(str.strip, line.split("="))
                    d[key] = val
            # Save this for later
            pickle_it('save', 'raspi_dict.pkl', d)

            # {
            # 'baseimage': 'raspios_arm64',
            # 'cpu': 'aarch64',
            # 'network': 'bitcoin',
            # 'chain': 'main',
            # 'fsexpanded': '1',
            # 'displayClass': 'hdmi',
            # 'displayType': '',
            # 'setupStep': '100',
            # 'fundRecovery': '0',
            # 'undervoltageReports': '0'}

            # Now we can get the bitcoin.conf data
            bitcoin_filename = '/mnt/hdd/bitcoin/bitcoin.conf'
            filename = open(bitcoin_filename, "r")
            for line in filename:
                if "=" in line:
                    key, val = map(str.strip, line.split("="))
                    d[key] = val

            # Save this for later
            pickle_it('save', 'raspi_bitcoin.pkl', d)

            # Try to get Current RaspiBlitz Version
            try:
                version_file = '/home/admin/_version.info'
                filename = open(version_file, "r")
                for line in filename:
                    if "=" in line:
                        key, val = map(str.strip, line.split("="))
                        d[key] = val
                rpi_version = d['codeVersion'].strip('"')
            except Exception:
                rpi_version = "<undetected>"
            spinner.ok("⚡ ")
            spinner.write(success("    RaspiBlitz Node Detected"))
            logging.info(f"[RaspiBlitz] Version {rpi_version}")

            config = load_config(quiet=True)
            if config['MAIN'].getboolean('output_to_monitor') is True:
                spinner.write(
                    success("    Switching Output to RaspiBlitz Monitor..."))
                try:
                    tty = '/dev/tty1'
                    redirect_tty(tty)
                except Exception as e:
                    logging.info(
                        error(
                            f"[RaspiBlitz] [IMPORTANT] Could not redirect output to the default monitor."
                        ))
                    logging.info(error(f"[RaspiBlitz] [IMPORTANT] Error: {e}"))
                    logging.info(
                        error(f"[RaspiBlitz] [IMPORTANT] Run at Terminal:"))
                    logging.info(
                        error(
                            f"[RaspiBlitz] [IMPORTANT] $ sudo chmod 666 /dev/tty1"
                        ))
                    logging.info(
                        error(
                            f"[RaspiBlitz] [IMPORTANT] to grant access and restart app."
                        ))

        except Exception:
            raspiblitz_detected = False
            spinner.fail("[i] ")
            spinner.write(warning("     Raspiblitz node not detected"))

        pickle_it('save', 'raspiblitz_detected.pkl', raspiblitz_detected)


def check_umbrel():
    # Let's check if running inside an Umbrel OS System
    # This is done by trying to access the getumbrel/manager container
    # and getting the environment variables inside that container
    print("")
    pickle_it('save', 'umbrel_detected.pkl', False)
    with yaspin(text="Checking if running inside Umbrel OS Node",
                color="green") as spinner:

        try:
            exec_command = [
                'docker', 'exec', 'middleware', 'sh', '-c', '"export"'
            ]
            result = subprocess.run(exec_command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            if result.returncode != 0:
                raise KeyError
            # Create a list split by ENTER
            result = result.stdout.decode('utf-8').split('\n')

            finder_list = [
                'BITCOIN_HOST', 'RPC_PASSWORD', 'RPC_PORT', 'RPC_USER',
                'HOSTNAME', 'DEVICE_HOSTS', 'PORT', 'LND_HOST', 'LND_NETWORK',
                'YARN_VERSION'
            ]
            # Ex:
            # declare -x BITCOIN_P2P_PORT="18444"
            finder_dict = {}
            for element in result:
                if any(env_var in element for env_var in finder_list):
                    elem_list = element.split('=', 1)
                    try:
                        elem_list[1] = elem_list[1].replace('"', '')
                        elem_list[1] = elem_list[1].replace("'", "")
                    except Exception:
                        pass
                    # Get the last item in the first string separated by space
                    # like BITCOIN_P2P_PORT above
                    value_item = elem_list[1]
                    key_item = elem_list[0].split(' ')[-1]
                    # Device hosts are usually split by commas:
                    if key_item == 'DEVICE_HOSTS':
                        value_item = value_item.split(',')
                    finder_dict[key_item] = value_item
            inside_umbrel = True
            pickle_it('save', 'umbrel_dict.pkl', finder_dict)
            spinner.ok("✅ ")
            spinner.write(success("    Running Umbrel OS"))
            logging.info("[Umbrel] Running Umbrel OS")
            config = load_config(True)
            if config['MAIN'].getboolean('output_to_monitor') is True:
                spinner.write(
                    success("    Switching Output to Umbrel Monitor..."))
                try:
                    tty = '/dev/tty1'
                    redirect_tty(tty)
                except Exception as e:
                    logging.info(
                        error(
                            "[UMBREL] [IMPORTANT] Could not redirect output to the default monitor."
                        ))
                    logging.info(error(f"[UMBREL] [IMPORTANT] Error: {e}"))
                    logging.info(
                        error(f"[UMBREL] [IMPORTANT] Run at Terminal:"))
                    logging.info(
                        error(
                            "[UMBREL] [IMPORTANT] $ sudo chmod 666 /dev/tty1"))
                    logging.info(
                        error(
                            "[UMBREL] [IMPORTANT] to grant access and restart app."
                        ))

        except Exception:
            inside_umbrel = False
            spinner.fail("[i] ")
            spinner.write(warning("     Umbrel OS not found"))

        pickle_it('save', 'inside_umbrel.pkl', inside_umbrel)

    #  Try to ping umbrel.local and check for installed apps
    print("")
    pickle_it('save', 'umbrel.pkl', inside_umbrel)
    mempool = False
    config = load_config(True)
    config_file = os.path.join(basedir, 'config.ini')
    try:
        if inside_umbrel is True:
            try:
                for host in finder_dict['DEVICE_HOSTS']:
                    if 'umbrel' in host:
                        url = host
                        break
                url = finder_dict['DEVICE_HOSTS'][1]
                # End URL in / if not there
                if url[-1] != '/':
                    url += '/'
                    if 'http' not in url:
                        url = 'http://' + url
            except Exception:
                url = config['UMBREL']['url']
        else:
            url = config['UMBREL']['url']
    except Exception:
        # As a last alternative, try the default
        url = 'http://umbrel.local/'

    with yaspin(text=f"Checking if Umbrel @ {url} is reachable",
                color="green") as spinner:
        # Test if this url can be reached
        try:
            result = tor_request(url)
            if not isinstance(result, requests.models.Response):
                raise Exception(f'Did not get a return from {url}')
            if not result.ok:
                raise Exception(f'Reached {url} but an error occured.')
            spinner.ok("✅ ")
            spinner.write(success(f"    Umbrel ☂️  found on {url}"))
            inside_umbrel = True
        except Exception as e:
            spinner.fail("[i] ")
            spinner.write(warning("     Umbrel not found:" + str(e)))

    if inside_umbrel:
        if 'onion' in url:
            url_parsed = ['[Hidden Onion address]']
        else:
            url_parsed = url
        logging.info(success(f"Umbrel running on {url_parsed}"))
        pickle_it('save', 'umbrel.pkl', inside_umbrel)
        with yaspin(text="Checking if Mempool.space app is installed",
                    color="green") as spinner:
            finder_dict = pickle_it('load', 'umbrel_dict.pkl')
            try:
                for host in finder_dict['DEVICE_HOSTS']:
                    if 'umbrel' in host:
                        url = host
                        break
                url = finder_dict['DEVICE_HOSTS'][1]
                # End URL in / if not there
                url += ':3006/'
                if 'http' not in url:
                    url = 'http://' + url
            except Exception:
                url = config['MEMPOOL']['url']

            try:
                result = tor_request(url)
                if not isinstance(result, requests.models.Response):
                    logging.error("[MEMPOOL] Could not connect to {url}")
                    raise Exception(f'Did not get a return from {url}')
                if not result.ok:
                    logging.error("[MEMPOOL] Could not connect to {url}")
                    raise Exception(
                        'Reached Mempool app but an error occured.')

                block_height = tor_request(url +
                                           '/api/blocks/tip/height').json()
                spinner.ok("✅ ")
                spinner.write(
                    success(
                        f"    Mempool.space app found on {url}. Latest block is: {block_height}"
                    ))
                logging.info(f"[MEMPOOL] Connected at {url}")
                mempool = True
            except Exception as e:
                logging.error("[MEMPOOL] Error {e}")
                spinner.fail("[i] ")
                spinner.write(warning("    " + str(e)))

    if mempool:
        config['MEMPOOL']['url'] = 'http://umbrel.local:3006/'
        with open(config_file, 'w') as configfile:
            config.write(configfile)


def check_specter():
    # CURRENTLY ONLY WORKS WHERE NO AUTH IS NEEDED
    # DEFAULT FOR UMBREL FOR EXAMPLE
    print("")
    pickle_it('save', 'specter_txs.pkl', None)
    with yaspin(text="Checking if Specter Server 👻 is running",
                color="green") as spinner:
        try:
            from specter_importer import Specter
            specter = Specter()
            txs = specter.refresh_txs(load=False)
            if '[Specter Error]' in txs:
                raise Exception(txs)
            pickle_it('save', 'specter_txs.pkl', txs)
            spinner.ok("✅ ")
            spinner.write(success("    Specter Server Running"))
            logging.info("[SPECTER] Specter Server Detected")
        except Exception:
            pickle_it('save', 'specter_txs.pkl', None)
            spinner.fail("[i] ")
            spinner.write(warning("     Specter Server not found"))
            logging.warning(
                "[WARN] Could not autodetect Specter Server. Check config.ini for settings."
            )


def check_os():
    try:
        rasp_file = '/sys/firmware/devicetree/base/model'
        with open(rasp_file, "r") as myfile:
            rasp_info = myfile.readlines()
    except Exception:
        rasp_info = 'Not a Raspberry Pi'
    os_info = {'uname': os.uname(), 'rpi': rasp_info}
    # Save for later
    pickle_it('save', 'os_info.pkl', os_info)


# Function to load and save data into pickles
def pickle_it(action='load', filename=None, data=None):
    import pickle
    home_path = os.path.dirname(os.path.abspath(__file__))
    filename = 'static/save/' + filename
    filename = os.path.join(home_path, filename)
    if action == 'delete':
        try:
            os.remove(filename)
            return ('deleted')
        except Exception:
            return ('failed')

    if action == 'load':
        try:
            with open(filename, 'rb') as handle:
                ld = pickle.load(handle)
                return (ld)
        except Exception:
            return ("file not found")
    else:
        try:
            with open(filename, 'wb') as handle:
                pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
                return ("saved")
        except Exception:
            return ('failed')


def redirect_tty(tty):
    try:
        with open(tty, 'rb') as inf, open(tty, 'wb') as outf:
            os.dup2(inf.fileno(), 0)
            os.dup2(outf.fileno(), 1)
            os.dup2(outf.fileno(), 2)
    except Exception:
        pass


def store_local_ip():
    try:
        from connections import get_local_ip
        ip = get_local_ip()
        pickle_it('save', 'ip.pkl', ip)
    except Exception:
        pickle_it('save', 'ip.pkl', None)


def main(quiet=None):
    # Store Local IP Address
    store_local_ip()
    # Main Variables
    if quiet is None:
        if 'quiet' in sys.argv:
            quiet = True
        else:
            quiet = False

    # if 'upgrade' in sys.argv:
    upgrade = True
    # else:
    # upgrade = False

    if quiet is False or quiet is None:
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
        check_version(upgrade)
        check_screen_size()
        check_cryptocompare()
        # Find if a node is present
        check_umbrel()
        check_raspiblitz()
        check_mynode()
        check_nodetype()
        check_specter()
        check_os()
        check_btc_rpc()
        login_tip()
        greetings()

    else:
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

    # Execute all data calls and save results locally so the main
    # app can run without interruptions while these updated as
    # background jobs
    # Separate background sequential jobs
    # depending on the nature of data getting gathered
    def price_grabs():
        data_btc_price(use_cache=False)

    def node_web_grabs():
        data_mempool(use_cache=False)
        data_large_block(use_cache=False)
        data_tor(use_cache=False)
        rpc_running = pickle_it('load', 'rpc_running.pkl')
        if rpc_running:
            data_btc_rpc_info(use_cache=False)
        data_random_satoshi(use_cache=False)
        specter_txs = pickle_it('load', 'specter_txs.pkl')
        if specter_txs is not None:
            data_specter(use_cache=False)

    def lower_priority_grabs():
        from connections import scan_network
        scan_network()

    def sys_grabs():
        data_login(use_cache=False)
        data_sys(use_cache=False)
        data_logger(use_cache=False)

    # Kick off data upgrades as background jobs
    try:
        price_refresh = config['MAIN'].getint('price_refresh_interval')
        if price_refresh is None:
            price_refresh = 15

    except Exception:
        price_refresh = 15

    job_defaults = {'coalesce': False, 'max_instances': 1}
    scheduler = BackgroundScheduler(job_defaults=job_defaults)
    scheduler.add_job(price_grabs, 'interval', seconds=price_refresh)
    scheduler.add_job(node_web_grabs, 'interval', seconds=15)
    scheduler.add_job(sys_grabs, 'interval', seconds=1)
    scheduler.add_job(lower_priority_grabs, 'interval', seconds=15)
    scheduler.start()
    print(success("✅  Background jobs starting. Please wait..."))
    main_dashboard(config, tor)
    scheduler.shutdown(wait=False)


if __name__ == '__main__':
    # Let's check users logged in and different TTY options
    # By default, outputs to console only but when running on a
    # node, it makes sense to output to the attached display
    tty = '/dev/tty'
    try:
        # Load TTY from config if changed
        config = load_config(quiet=True)
        tty = config['MAIN'].get('tty')
        # Redirect tty output
        if tty != '/dev/tty':
            redirect_tty(tty)

    except Exception as e:
        print(
            warning(
                f"    [!] Could not redirect to selected output {tty}. Error: {e} "
            ))
        logging.error(f"[ERROR] Could not connect to {tty}. Error {e}.")

    main()
    goodbye()
