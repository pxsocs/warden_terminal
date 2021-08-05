import ast
import os
import sys
import subprocess
import emoji
import pickle
import pathlib

from requests.api import request
import pyfiglet

import pyttsx3
import logging
from tabulate import tabulate
from random import randrange

from datetime import datetime, timedelta
from dateutil import parser

from connections import test_tor, tor_request
from ansi_management import (warning, success, error, info, bold, jformat,
                             muted, time_ago, cleanfloat, yellow)

from pricing_engine import multiple_price_grab, GBTC_premium, fxsymbol


def data_tor(tor=None, use_cache=True):
    if use_cache is True:
        cached = pickle_it('load', 'data_tor.pkl')
        if cached != 'file not found' and cached is not None:
            return (cached)

    from node_warden import load_config
    config = load_config(quiet=True)
    if not tor:
        tor = test_tor()

    import socket
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        local_ip = 'Error getting local IP'

    if not config['MAIN'].getboolean('hide_private_info'):
        tor_string = f"""   {success('TOR Connected')}
    Running on port {info(bold(tor['port']))}
    Tor IP Address {warning(tor['post_proxy']['origin'])}
    Ping Time {tor['post_proxy_ping']}
    Global IP Address {warning(tor['pre_proxy']['origin'])}
    Ping Time {muted(tor['pre_proxy_ping'])}
    Local IP Address {warning(local_ip)}
    """
    else:
        tor_string = f"""   {success('TOR Connected')}
    Running on port {info(bold(tor['port']))}
    Tor IP Address {yellow('** HIDDEN **')}
    Ping Time {tor['post_proxy_ping']}
    Global IP Address {yellow('** HIDDEN **')}
    Ping Time {muted(tor['pre_proxy_ping'])}
    Local IP Address {yellow('** HIDDEN **')}
    """
    pickle_it('save', 'data_tor.pkl', tor_string)
    return (tor_string)


def data_login(use_cache=True):
    if use_cache is True:
        cached = pickle_it('load', 'data_login.pkl')
        if cached != 'file not found' and cached is not None:
            return (cached)
    tabs = []
    try:
        processes = subprocess.check_output("last")
        processes = list(processes.splitlines())
    except Exception as e:
        tabs = muted(
            f'List of users logged in to this computer could not be retrieved. Error {e}'
        )
        return tabs
    for process in processes:
        try:
            process = process.decode("utf-8")
            if 'still' not in process or 'boot' in process:
                continue
            user = process.split()[0]
            process = process.replace(user, '')
            console = process.split()[0]
            process = process.replace(console, '')
            date_str = parser.parse(process, fuzzy=True)
            # Check if someone logged in the last 60 minutes
            expiration = 60
            too_soon = datetime.now() - timedelta(minutes=expiration)
            if date_str > too_soon:
                warn = warning(emoji.emojize(':warning:'))
                tabs.append([
                    f" {warn} {error(f'Recent Login (last {expiration} min)')}:"
                ])
            tabs.append([
                f"   {warning(user)} at {muted(console)} " + bold(
                    f"logged on {success(date_str.strftime('%H:%M (%b-%d)' ))}"
                )
            ])
        except Exception:
            tabs.append([f"  {process}"])
    if tabs != []:
        tabs = tabulate(tabs,
                        headers=['Users Logged in to this computer'],
                        colalign=["left"])
    else:
        tabs = muted(
            'List of users logged in to this computer is empty.\nEither no outside users are logged in or login info is not available.'
        )

    pickle_it('save', 'data_login.pkl', tabs)
    return (tabs)


def btc_price_data():
    try:
        price_data = pickle_it('load', 'multi_price.pkl')
        # test if loaded. Will raise KeyError if not.
        _ = price_data['DISPLAY']
    except Exception:
        price_data = 'loading...'
    return (price_data)


def data_large_price(price=None, change=None, chg_str=None, moscow_time=False):
    from node_warden import load_config
    config = load_config(quiet=True)
    ft_config = config['MAIN']
    font = ft_config.get('large_text_font')
    # If a price is provided, it won't refresh
    if price is not None:
        btc_price = price
        if change is None:
            chg = -1
            chg_str = '-'

    else:
        btc = btc_price_data()
        custom_fig = pyfiglet.Figlet(font=font)
        if btc != 'loading...':
            try:
                btc_price = cleanfloat(btc['DISPLAY']['BTC']['USD']['PRICE'])
            except Exception:
                btc_price = None
                return (error(' >> Error getting price data. Retrying...'))
        else:
            btc_price = btc
            return_fig = custom_fig.renderText('Loading...')
            return (return_fig)

    if moscow_time is True:
        moscow_price = 100000000 / btc_price
        return_fig = yellow(custom_fig.renderText(jformat(moscow_price, 0)))
        return_fig += muted('\nSats per dollar\n')
        # return_fig += muted('Moscow Time')
        return (return_fig)

    return_fig = custom_fig.renderText('$  ' + jformat(btc_price, 0))
    return_fig = yellow(return_fig)

    if chg_str != '-':
        chg_str = btc['DISPLAY']['BTC']['USD']['CHANGEPCTDAY']
        chg = cleanfloat(chg_str)

    if chg_str != '-':
        msg = '\n'
        if chg >= 0:
            msg += '24hr Change: ' + success(f'{chg_str}%\n')
        if chg > 5:
            msg += (muted("[NgU] ") +
                    success("Looks like Bitcoin is pumping "))

        if chg < 0:
            msg += '24hr Change: ' + error(f'{chg_str}%\n')
        if chg < -5:
            msg += muted("Good time to stack some sats")

    return_fig = muted(return_fig)
    return_fig += msg

    position = 0
    try:
        if config['MAIN'].get('hide_private_info') is True:
            raise Exception('Not displaying position - hidden')
        position = config['PORTFOLIO'].getfloat('position_btc')
        if position == '' or position is None:
            raise Exception('No BTC Position Found')
        if position != 0:
            price_str = btc_price
            value = cleanfloat(price_str) * position
            sats = False
            decs = 4
            if position < 1 and position > -1:
                sats = True
                position = position * 100000000
                decs = 0
            position_str = jformat(position, decs)

            if sats is True:
                position_str += ' sats'
            else:
                position_str = '₿ ' + position_str

            position_tab = []
            position_tab.append(
                ['Portfolio', position_str, '$ ' + jformat(value, 2)])

            position_tabs = tabulate(position_tab,
                                     colalign=["left", "center", "right"])

            return_fig += '\n\n' + position_tabs

    except Exception:
        pass

    return (return_fig)


def data_large_block(use_cache=True):
    block_time = pickle_it('load', 'recent_block.pkl')

    if use_cache is True:
        cached = pickle_it('load', 'data_large_block.pkl')
        if cached != 'file not found' and cached is not None:
            if block_time is not None:
                if block_time != 'file not found':
                    minutes_ago = (datetime.now() -
                                   datetime.fromtimestamp(block_time))
                    minutes_ago = minutes_ago.seconds // 60 % 60
                    # Source for these ranges:
                    # https://www.reddit.com/r/btc/comments/6v5ee7/block_times_and_probabilities/
                    clr_txt = ''
                    if minutes_ago < 10:
                        clr_txt = success(time_ago(block_time))
                    elif (minutes_ago >= 10) and (minutes_ago <= 20):
                        clr_txt = warning(time_ago(block_time))
                    elif minutes_ago > 20:
                        clr_txt = error(time_ago(block_time))
                    elif minutes_ago > 50 and minutes_ago < 90:
                        clr_txt += '\nThis is a slow block but expected to happen once a day'
                    elif minutes_ago >= 90 and minutes_ago < 120:
                        clr_txt += '\nThis is a slow block.\n90min blocks are expected to happen\nonly once every 2 months'
                    elif minutes_ago >= 120:
                        clr_txt += '\nThis is a VERY slow block.\n120min blocks are expected to happen\nonly once every 3 years'
                    txt = f"\n\n Block mined {clr_txt}"
                    cached += txt

            return (cached)

    from node_warden import load_config
    config = load_config(quiet=True)
    ft_config = config['MAIN']
    font = ft_config.get('large_text_font')
    # If a price is provided, it won't refresh
    latest_block = pickle_it(action='load', filename='block.pkl')

    custom_fig = pyfiglet.Figlet(font=font)
    return_fig = custom_fig.renderText(jformat(latest_block, 0))
    return_fig = yellow(return_fig)
    return_fig += muted("Block Height")

    pickle_it('save', 'data_large_block.pkl', return_fig)

    if block_time is not None:
        if block_time != 'file not found':
            minutes_ago = (datetime.now() - datetime.fromtimestamp(block_time))
            minutes_ago = minutes_ago.seconds // 60 % 60
            # Source for these ranges:
            # https://www.reddit.com/r/btc/comments/6v5ee7/block_times_and_probabilities/
            clr_txt = ''
            if minutes_ago < 10:
                clr_txt = success(time_ago(block_time))
            elif (minutes_ago >= 10) and (minutes_ago <= 20):
                clr_txt = warning(time_ago(block_time))
            elif minutes_ago > 20:
                clr_txt = error(time_ago(block_time))
            elif minutes_ago > 50 and minutes_ago < 90:
                clr_txt += '\nThis is a slow block but expected to happen once a day'
            elif minutes_ago >= 90 and minutes_ago < 120:
                clr_txt += '\nThis is a slow block.\n90min blocks are expected to happen\nonly once every 2 months'
            elif minutes_ago >= 120:
                clr_txt += '\nThis is a VERY slow block.\n120min blocks are expected to happen\nonly once every 3 years'
            txt = f"\n\n Block mined {clr_txt}"
            return_fig += txt

    return (return_fig)


def data_large_message(use_cache=True):
    # Displays a custom message saved on config.ini
    # under [MAIN][message_widget]
    from node_warden import load_config
    config = load_config(quiet=True)
    ft_config = config['MAIN']
    font = 'small'
    try:
        message = ft_config.get('message_widget')
    except Exception:
        return None
    # If a price is provided, it won't refresh
    xs_display = pickle_it('load', 'xs_display.pkl')
    try:
        if xs_display is not True:
            custom_fig = pyfiglet.Figlet(font=font)
            return_fig = custom_fig.renderText(message)
        else:
            return_fig = message
    except Exception:
        custom_fig = pyfiglet.Figlet(font=font)
        return_fig = custom_fig.renderText(message)

    return_fig = yellow(return_fig)
    return (return_fig)


def data_specter(use_cache=True):
    from node_warden import load_config
    config = load_config(quiet=True)
    if use_cache is True:
        cached = pickle_it('load', 'data_specter.pkl')
        if cached != 'file not found' and cached is not None:
            refresh_time = pickle_it('load', 'specter_refresh.pkl')
            if refresh_time != "file not found" or refresh_time is not None:
                cached += success(
                    f'\n\nLast server connection: {time_ago(refresh_time)}')
            return (cached)

    # Refresh Txs
    try:
        from specter_importer import Specter
        specter = Specter()
        txs = specter.refresh_txs(load=False)
        if '[Specter Error]' in txs:
            return 'Error getting transactions'
        pickle_it('save', 'specter_txs.pkl', txs)
        # Save latest refresh time
        pickle_it('save', 'specter_refresh.pkl', datetime.now())
    except Exception:
        txs = None
        return

    # Txs found, now get relevant data and format for output
    hidden = config['MAIN'].getboolean('hide_private_info')
    font = config['MAIN'].get('large_text_font')
    last_tx_time = 0
    last_tx_block = 0
    balance = 0
    return_fig = ""

    for tx in txs['txlist']:
        if tx['category'] == 'send':
            multiplier = -1
        else:
            multiplier = 1
        balance += tx['amount'] * multiplier
        if tx['blockheight'] > last_tx_block:
            last_tx_block = tx['blockheight']
        if tx['time'] > last_tx_time:
            last_tx_time = tx['time']

    ft_config = config['MAIN']
    font = ft_config.get('large_text_font')
    custom_fig = pyfiglet.Figlet(font=font)

    return_fig = 'Specter Server Balance\n'
    return_fig += '----------------------\n'

    if balance < 1:
        balance = jformat(balance * 100000000, 0)
        sats = True
    else:
        balance = jformat(balance, 4)
        sats = False

    if hidden is False:
        return_fig += custom_fig.renderText(balance)
        if sats is True:
            return_fig += "Sats\n"
        else:
            return_fig += "Bitcoin\n"
        return_fig = yellow(return_fig)

    else:
        return_fig += ('<Balance Hidden>')
        return_fig = yellow(return_fig)
        return_fig += "\nPress 'H' to display\n\n"

    return_fig += f'Last activity at block {jformat(last_tx_block, 0)}'
    current_block = pickle_it('load', 'block.pkl')
    if current_block != 'file not found':
        return_fig += f'\n{jformat(current_block - last_tx_block, 0)} blocks ago'

    tx_time = datetime.fromtimestamp(last_tx_time)
    return_fig += f'\non {tx_time}\n{time_ago(tx_time)}'

    # Check if txs in last 24hrs
    difference = datetime.now() - tx_time
    if difference.days == 0:
        return_fig += "\n\n----------------------------------------"
        return_fig += warning("\n[!] RECENT TRANSACTIONS FOUND (24 hours)")
        return_fig += "\n----------------------------------------"

    pickle_it('save', 'data_specter.pkl', return_fig)

    refresh_time = pickle_it('load', 'specter_refresh.pkl')
    if refresh_time != "file not found" or refresh_time is not None:
        return_fig += success(
            f'\n\nLast server connection: {time_ago(refresh_time)}')

    return (return_fig)


def data_btc_price(use_cache=True):
    if use_cache is True:
        cached = pickle_it('load', 'data_btc_price.pkl')
        if cached != 'file not found' and cached is not None:
            last_price_refresh = pickle_it('load', 'last_price_refresh.pkl')
            if last_price_refresh != 'file not found':
                cached += (
                    f"\n\nLast refresh: {success(time_ago(last_price_refresh))}"
                )
            return (cached)

    from node_warden import load_config
    config = load_config(quiet=True)
    fx_config = config['CURRENCIES']
    currencies = ast.literal_eval(fx_config.get('fx_list'))
    primary_fx = ast.literal_eval(fx_config.get('primary_fx'))
    price_data = multiple_price_grab('BTC', ','.join(currencies))
    # save BTC prices to be used with all apps.
    # All refreshes are done at this single point to avoid
    # different prices and reduce the number of API calls
    pickle_it('save', 'multi_price.pkl', price_data)
    last_price_refresh = datetime.now()
    pickle_it('save', 'last_price_refresh.pkl', last_price_refresh)
    # Get prices in different currencies
    tabs = []
    btc_usd_price = 0

    # Get Update Time
    try:
        r_time = pickle_it('load', 'last_price_refresh.pkl')
    except Exception:
        r_time = warning("Loading...")
    try:
        r_time = time_ago(r_time)
    except Exception:
        r_time = warning("Error")

    for fx in currencies:
        try:
            try:
                price_str = price_data['RAW']['BTC'][fx]['PRICE']
                price_str = fxsymbol(fx) + jformat(price_str, 2)
                high = price_data['RAW']['BTC'][fx]['HIGHDAY']
                high = fxsymbol(fx) + jformat(high, 0)
                low = price_data['RAW']['BTC'][fx]['LOWDAY']
                low = fxsymbol(fx) + jformat(low, 0)
            except Exception:
                price_str = price_data['DISPLAY']['BTC'][fx]['PRICE']
                high = price_data['DISPLAY']['BTC'][fx]['HIGHDAY']
                low = price_data['DISPLAY']['BTC'][fx]['LOWDAY']

            chg_str = price_data['DISPLAY']['BTC'][fx]['CHANGEPCTDAY']
            market = muted(price_data['DISPLAY']['BTC'][fx]['LASTMARKET'])
            try:
                chg = float(chg_str)
                if chg >= 0:
                    chg_str = success('+' + chg_str + '%')
                elif chg < 0:
                    chg_str = error(chg_str + '%')
            except Exception:
                chg_str = muted(chg_str + '%')

            if fx == 'USD':
                btc_usd_price = cleanfloat(price_str)

            if fx == primary_fx:
                fx = info(fx)

            xs_display = pickle_it('load', 'xs_display.pkl')
            try:
                if xs_display is True:
                    tabs.append([u'  ' + fx, price_str, chg_str, market])
                else:
                    xs_display = False
                    tabs.append([
                        u'  ' + fx, price_str, chg_str, low + ' - ' + high,
                        market
                    ])
            except Exception:
                xs_display = False
                tabs.append([
                    u'  ' + fx, price_str, chg_str, low + ' - ' + high, market
                ])

        except Exception as e:
            tabs.append(['error: ' + str(e)])

    if tabs == []:
        return (
            error(' >> Error getting data from CryptoCompare. Retrying...'))

    try:
        if xs_display is False:
            tabs = tabulate(
                tabs,
                headers=['Fiat', 'Price', '% change', '24h Range', 'Source'],
                colalign=["center", "right", "right", "center", "right"])
        else:
            tabs = tabulate(tabs,
                            headers=['Fiat', 'Price', '% change', 'Source'],
                            colalign=["center", "right", "right", "right"])
    except Exception:
        return (
            error(' >> Error getting data from CryptoCompare. Retrying...'))

    # GBTC
    gbtc_config = config['STOCKS']
    try:
        if gbtc_config.getboolean('GBTC_enabled'):
            tabs += '\n\n'
            gbtc_url = 'https://finnhub.io/api/v1/quote?symbol=GBTC&token=bvfhuqv48v6rhdtvnks0'
            gbtc_data = tor_request(gbtc_url).json()
            gbtc_tabs = []
            GBTC_shares = gbtc_config.getfloat('gbtc_shares')
            fairvalue, premium = (GBTC_premium((gbtc_data['c']), btc_usd_price,
                                               GBTC_shares))

            if premium * 1 > 0:
                premium = success('+' + jformat(premium, 2, 0.01) + '%')
            elif premium * 1 < 0:
                premium = error(jformat(premium, 2, 0.01) + '%')

            fairvalue = jformat(fairvalue, 2)

            chg_str = gbtc_data['c'] / gbtc_data['pc']
            try:
                chg = (chg_str)
                if chg > 0:
                    chg_str = success('+' + jformat(chg, 2) + ' %')
                elif chg < 0:
                    chg_str = error(jformat(chg, 2) + ' %')
            except Exception:
                chg_str = muted(chg_str)

            gbtc_tabs.append([
                'GBTC',
                jformat(gbtc_data['c'], 2), chg_str, premium, fairvalue,
                time_ago(gbtc_data['t'])
            ])
            gbtc_tabs = tabulate(
                gbtc_tabs,
                headers=['Ticker', 'Price', '%', 'Premium', 'Fair', 'Update'],
                colalign=["left", "right", "right", "right", "right", "right"])
            tabs += gbtc_tabs

    except Exception as e:
        er_st = error(f' Error getting GBTC data: {e}')
        tabs += er_st

    position = 0
    try:
        if config['MAIN'].get('hide_private_info') is True:
            raise Exception('Not displaying position - hidden')
        position = config['PORTFOLIO'].getfloat('position_btc')
        if position == '' or position is None:
            raise Exception('No BTC Position Found')
        if position != 0:
            price_str = price_data['RAW']['BTC']['USD']['PRICE']
            value = cleanfloat(price_str) * position
            sats = False
            decs = 4
            if position < 1 and position > -1:
                sats = True
                position = position * 100000000
                decs = 0
            position_str = jformat(position, decs)

            if sats is True:
                position_str += ' sats'
            else:
                position_str = '₿ ' + position_str

            position_tab = []
            position_tab.append(
                ['Portfolio', position_str, '$ ' + jformat(value, 2)])

            position_tabs = tabulate(position_tab,
                                     colalign=["left", "center", "right"])

            tabs += '\n\n' + position_tabs

    except Exception:
        pass

    pickle_it('save', 'data_btc_price.pkl', tabs)

    tabs += (f"\n\nLast refresh: {success(time_ago(last_price_refresh))}")

    return tabs


def data_sys(use_cache=True):
    if use_cache is True:
        cached = pickle_it('load', 'data_sys.pkl')
        if cached != 'file not found' and cached is not None:
            return (cached)

    tabs = []
    os_info = pickle_it('load', 'os_info.pkl')
    umbrel = pickle_it('load', 'umbrel.pkl')

    if os_info == 'file not found':
        return "Error Getting Files"

    # Get OS info
    tabs.append([
        " OS / System",
        os_info["uname"].sysname + ' / ' + os_info["uname"].machine
    ])
    if os_info["rpi"] != 'Not a Raspberry Pi':
        tabs.append([" Raspberry Pi", os_info["rpi"][0]])
    if umbrel:
        tabs.append([" Umbrel Node found @", 'http://umbrel.local/'])

    try:
        import psutil
        last_boot = psutil.boot_time()
        tabs.append(
            ["  Last Boot Time",
             time_ago(datetime.fromtimestamp(last_boot))])

    except Exception:
        pass

    tabs = tabulate(tabs, colalign=["left", "right"])

    tabs += '\n\nSystem Resources\n----------------'

    # Get current size of window
    rows, columns = subprocess.check_output(['stty', 'size']).split()
    small_display = pickle_it('load', 'small_display.pkl')
    if small_display:
        bar_size = int(int(columns)) - 35
    else:
        bar_size = int(int(columns) / 3) - 35

    # Create CPU Temperature Bar
    try:
        import psutil
        temp_result = psutil.sensors_temperatures()
        temp_result = round(temp_result['cpu_thermal'][0].current, 2)
        # RPI temperature guidelines:
        # https://www.raspberrypi.org/documentation/faqs/#pi-performance
        temp_bar = printProgressBar(
            iteration=temp_result,
            total=80,
            prefix='CPU Temperature',
            suffix=
            f'{temp_result}°C\n                 (ideal range = 0°C to 70°C)',
            length=bar_size,
            unit='°C',
            perc=False,
            printEnd='',
            max_min=(0, 70))
        tabs += f'\n{temp_bar}'
    except Exception:
        pass

    # Create CPU Usage Bar
    try:
        import psutil
        cpu_result = psutil.cpu_percent(interval=0.1)
        cpu_result = round(cpu_result, 2)
        cpu_bar = printProgressBar(iteration=cpu_result,
                                   total=100,
                                   prefix='CPU Usage      ',
                                   suffix=f'{cpu_result}%',
                                   length=bar_size,
                                   perc=True,
                                   printEnd='',
                                   max_min=(0, 85))

    except Exception:
        cpu_bar = warning('[i] Could not retrieve CPU Usage')

    tabs += f'\n{cpu_bar}'

    # Create Memory Usage Bar
    try:
        import psutil
        mem_result = psutil.virtual_memory()
        mem_bar = printProgressBar(
            iteration=round(mem_result.percent, 2),
            total=100,
            prefix='Memory Usage   ',
            suffix=
            f'{round(mem_result.percent, 2)}%\n                 Total Memory {round(mem_result.total/1000000000,0)} GB',
            length=bar_size,
            perc=True,
            printEnd='',
            max_min=(0, 85))

    except Exception:
        mem_bar = warning('[i] Could not retrieve Memory Usage')

    tabs += f'\n{mem_bar}'

    # Create Disk Usage Bar(s)
    # Get list of devices
    tabs += '\n\nStorage\n---------------'
    try:
        import shutil
        partitions = ['/mnt/data', 'mnt/hdd', '/mnt/storage']

        for partition in partitions:
            try:
                total, used, free = shutil.disk_usage(partition)
                # Get partition name and truncate / fix size
                prefix = str(partition)
                prefix = '{:<15}'.format(prefix[:15])
                perc_c = 100 - ((free / total) * 100)
                disk_bar = printProgressBar(
                    iteration=round(perc_c, 2),
                    total=100,
                    prefix=prefix,
                    suffix=
                    (f'{round(perc_c, 2)}%' +
                     f'\n                 {round(free / (10**9), 2)} GB available of {round(total / (10 ** 9), 2)} GB'
                     ),
                    length=bar_size,
                    perc=True,
                    printEnd='',
                    max_min=(0, 90))

                tabs += f'\n{disk_bar}'

            except Exception:
                pass

    except Exception:
        disk_bar = warning('[!] Could not retrieve Disk Usage')

    pickle_it('save', 'data_sys.pkl', tabs)
    return (tabs)


# Print progress bar
def printProgressBar(iteration,
                     total,
                     prefix='',
                     suffix='',
                     decimals=2,
                     length=100,
                     fill='█',
                     unit='%',
                     perc=True,
                     max_min=None,
                     printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        unit        - Optional  : Unit of account (Str)
        perc        - Optional  : True to display percentages, False in absolutes (Bool)
        max_min     - Optional  : Tuple with max and min values to warn (Tuple)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    if perc:
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        if max_min is not None:
            if iteration > max_min[1] or iteration < max_min[0]:
                prefix = error(prefix)
                bar = warning(bar)
            else:
                prefix = success(prefix)
                bar = success(bar)
        return (f'{prefix} |{bar}| {suffix} {printEnd}')

    else:
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        if max_min is not None:
            if iteration > max_min[1] or iteration < max_min[0]:
                prefix = error(prefix)
                bar = warning(bar)
            else:
                prefix = success(prefix)
                bar = success(bar)
        return (f'{prefix} |{bar}| {suffix} {printEnd}')


def data_mempool(use_cache=True):
    if use_cache is True:
        cached = pickle_it('load', 'data_mempool.pkl')
        if cached != 'file not found' and cached is not None:
            return (cached)
    from node_warden import load_config

    config = load_config(quiet=True)
    mp_config = config['MEMPOOL']
    url = mp_config.get('url')
    tabs = []

    # Get recommended fees
    forced_mps = False
    try:
        mp_fee = tor_request(url + '/api/v1/fees/recommended').json()
    except Exception:
        try:
            url = 'http://mempool.space'
            mp_fee = tor_request(url + '/api/v1/fees/recommended').json()
            forced_mps = True
        except Exception as e:
            return (
                error(f' >> Error getting data from {url}. Retrying... {e}'))

    tabs = list(mp_fee.values())
    tabs = [[str(x) + ' sats/Vb' for x in tabs]]
    tabs = tabulate(tabs,
                    headers=["Fastest Fee", "30 min fee", "1 hour fee"],
                    colalign=["center", "center", "center"])
    try:
        block_height = tor_request(url + '/api/blocks/tip/height').json()
    except Exception:
        return (error(f' >> Error getting data from {url}. Retrying...'))
    # Save the latest block height
    saved_block = pickle_it(action='load', filename='block.pkl')
    if (saved_block != block_height) and (
            config['MEMPOOL'].getboolean('block_found_sound')):
        # Block found play sound
        try:
            if config['MAIN'].getboolean('sound'):
                engine = pyttsx3.init()
                engine.setProperty('rate', 270)
                engine.say(config['MEMPOOL'].get('block_found_txt'))
                engine.runAndWait()
        except Exception:
            pass
        logging.info(
            info('[MEMPOOL] ') +
            success("A new Bitcoin Block was just found. ") +
            yellow("'Tick. Tock. Next block.'"))

    pickle_it(action='save', filename='block.pkl', data=block_height)

    block_txt = success(f' Block Height: {jformat(block_height, 0)}\n\n')
    tabs = block_txt + info(' Mempool Fee Estimates: \n') + tabs

    try:
        mp_blocks = tor_request(url + '/api/blocks').json()
    except Exception:
        return (error(" >> Error getting Mempool data. Retrying..."))

    mp_tabs = []
    gradient_color = 0
    try:
        pickle_it('save', 'recent_block.pkl', mp_blocks[0]['timestamp'])
    except Exception:
        pickle_it('save', 'recent_block.pkl', None)

    for block in mp_blocks:
        mp_tabs.append([
            time_ago(block['timestamp']),
            jformat(block['height'], 0),
            jformat(block['tx_count'], 0),
            jformat(block['size'], 2, 1000000) + ' MB'
        ])
        gradient_color += 1

    mp_tabs = tabulate(mp_tabs,
                       headers=[" Time", "Height", "Tx Count", "Size"],
                       colalign=["right", "center", "center", "right"])
    tabs += info('\n\n Latest Blocks: \n') + mp_tabs
    if not forced_mps:
        tabs += muted(f"\n\n Source: {url} \n")
    else:
        tabs += warning(f"\n\n [!] Source: {url} [Alternate]")
    pickle_it('save', 'data_mempool.pkl', tabs)
    return tabs


def data_whitepaper():
    logging.info("Downloading Whitepaper >> bitcoin.pdf")
    from rpc import get_whitepaper
    try:
        wp = get_whitepaper()
        if 'Success' not in wp:
            message = f"Failed to get Whitepaper from your own node. Will download. Error: {wp}."
            logging.error('[WARN] ' + message)
            raise Exception(message)
        return (wp)
    except Exception:
        try:
            from pathlib import Path
            filename = Path('bitcoin.pdf')
            url = 'https://bitcoin.org/bitcoin.pdf'
            response = tor_request(url)
            filename.write_bytes(response.content)
            logging.info(
                success(
                    "File bitcoin.pdf saved but downloaded from Bitcoin.org [Success]"
                ))
        except Exception as e:
            logging.error(
                warning(
                    f"    Could not download bitcoin.pdf >> error: {e} [ERROR]"
                ))


def data_logger(use_cache=True):
    if use_cache is True:
        cached = pickle_it('load', 'data_logger.pkl')
        if cached != 'file not found' and cached is not None:
            return (cached)

    from node_warden import debug_file
    try:
        lines = 40
        log_txt = tail(debug_file, lines)
        return_str = []
        for element in log_txt:
            if 'INFO' in element:
                return_str.append(info(element))
            elif 'ERROR' in element:
                return_str.append(error(element))
            elif 'WARN' in element:
                return_str.append(warning(element))
            else:
                return_str.append((element))
        return_str = ''.join(return_str)
    except Exception:
        return yellow('>> Error Loading Log Messages. Retying...')
    pickle_it('save', 'data_logger.pkl', return_str)
    return return_str


def data_random_satoshi(use_cache=True):
    if use_cache is True:
        cached = pickle_it('load', 'data_satoshi.pkl')
        if cached != 'file not found' and cached is not None:
            return (cached)
    from node_warden import load_config
    config = load_config(quiet=True)
    url = config['QUOTES'].get('url')
    try:
        load_quote = pickle_it('load', 'satoshi.pkl')
        if load_quote == "file not found":
            quotes = tor_request(url).json()
            pickle_it('save', 'satoshi.pkl', quotes)
        else:
            quotes = load_quote
    except Exception:
        return (error(' >> Error contacting server. Retrying... '))
    quote = quotes[randrange(len(quotes))]
    return_str = info(f"Satoshi Quotes | Subject: {quote['category']}\n")
    return_str += muted(f"{quote['date']} on {quote['medium']}\n")
    return_str += yellow(f"{quote['text']} \n\n")
    return_str += muted("Source: Nakamoto Institute")
    pickle_it('save', 'data_satoshi.pkl', return_str)
    return (return_str)


def data_umbrel(umbrel=True):
    from node_warden import load_config
    config = load_config(quiet=True)
    if umbrel is None:
        umbrel = pickle_it('load', 'umbrel.pkl')
    if umbrel is not True:
        return None

    from welcome import umbrel
    umbrel_logo = umbrel()
    url = config['UMBREL'].get('url')
    umbrel_info = f"\n\t    \nUmbrel Node Running\nurl: {url} \nsynched: 100%"
    tabs = [[umbrel_logo, umbrel_info]]
    tabs = tabulate(tabs, colalign=["none", "right"], tablefmt="plain")
    return (tabs)


def data_btc_rpc_info(use_cache=True):
    from node_warden import pickle_it
    # Check if getting data from RPC or from RPC Explorer
    rpc_connection = pickle_it('load', 'rpc_connection.pkl')
    url = None
    if rpc_connection is not None and rpc_connection != 'file not found':
        # Get Blockchaininfo from Bitcoin RPC
        bci = rpc_connection.getblockchaininfo()
        network = rpc_connection.getnetworkinfo()
        uptime = rpc_connection.uptime()
        wallets = rpc_connection.getbalances()
        txs = rpc_connection.listtransactions()
    else:
        # Let's try from RPC Explorer at port 3002
        from connections import is_service_running
        rpce_running, host_data = is_service_running('Bitcoin RPC Explorer')
        if rpce_running is True:
            url = host_data[0][0][0]
            data = pickle_it('load', f'btcrpc_json_{url}.pkl')
            if data == 'file not found':
                return ("Loading data...")
            # Last refresh time
            refresh = pickle_it('load', f'btcrpc_refresh_{url}.pkl')
            try:
                network = bci = data['node-details']
                uptime = data['node-details']['timemillis'] / 60000000
                uptime = datetime.now() - timedelta(minutes=uptime)
                uptime = time_ago(uptime)
                wallets = None
                txs = None
            except Exception as e:
                return (f"Error getting {url} info: {e}")

    # Check if small or large and the size of progress  bars
    rows, columns = subprocess.check_output(['stty', 'size']).split()
    small_display = pickle_it('load', 'small_display.pkl')
    if small_display:
        bar_size = int(int(columns)) - 38
    else:
        bar_size = int(int(columns) / 3) - 38

    tabs = []

    # Testnet, Mainnet, etc...
    tabs.append(["Chain", bci['chain']])

    # Create Synch progress bar
    try:
        perc_c = float(bci['verificationprogress']) * 100
        perc_c = 100 if perc_c > 99.95 else perc_c
        synch_bar = printProgressBar(iteration=round(perc_c, 2),
                                     total=100,
                                     suffix=(f'{round(perc_c, 2)}%'),
                                     length=bar_size,
                                     perc=True,
                                     printEnd='',
                                     max_min=(0, 100))
    except Exception:
        synch_bar = "Error checking synch completion"

    pickle_it('save', 'synch_status.pkl', [synch_bar, perc_c])

    tabs.append(["Synch", synch_bar])

    # Uptime

    try:
        tabs.append(["Uptime", f"{uptime}"])
    except Exception:
        pass

    # Initial BLOCK Download & other info

    tabs.append(["Blockchain Size", humanbytes(bci['size_on_disk'])])
    pruned = bci['pruned']
    if pruned is True:
        tabs.append(["Prunned", warning("Prunned [!]")])
    else:
        tabs.append(["Prunned", "Not Prunned"])
    try:
        segwit = bci['softforks']['segwit']['active']
        if segwit is True:
            tabs.append(["Segwit", success("Ready")])
    except Exception:
        pass
    try:
        taproot = bci['softforks']['taproot']['active']
        if taproot is True:
            tabs.append(["Taproot", success("Ready")])
    except Exception:
        pass

    # Network Info
    tabs.append([muted("Network Info"), ""])
    tabs.append(['Bitcoin Core Version', network['subversion']])
    tabs.append(['Connections', jformat(network['connections'], 0)])

    # Wallet Info
    wallets = False
    try:
        any_wallets = rpc_connection.listwallets()
        if any_wallets == []:
            tabs.append(["Wallets", "No Wallets Found"])
            wallets = False
        else:
            try:
                confirmed = float(wallets['mine']['trusted'])
            except Exception:
                confirmed = 0
            try:
                unconfirmed = float(wallets['mine']['immature'])
            except Exception:
                unconfirmed = 0
            from node_warden import load_config
            config = load_config(quiet=True)
            if not config['MAIN'].getboolean('hide_private_info'):
                total = confirmed + unconfirmed
                tabs.append(["Confirmed", jformat(confirmed, 8)])
                tabs.append(["Unconfirmed", jformat(unconfirmed, 8)])
                tabs.append(["Total", jformat(total, 8)])
            else:
                tabs.append(["Confirmed", yellow("** HIDDEN **")])
                tabs.append(["Unconfirmed", yellow("** HIDDEN **")])
                tabs.append(["Total", yellow("** HIDDEN **")])

            wallets = True

    except Exception:
        wallets = False

    # Transaction Info
    if wallets is True:
        max_time = 0
        try:
            for tx in txs:
                if tx['time'] > max_time:
                    max_time = tx['time']
        except Exception:
            max_time = 0

        if max_time > 0:
            time_max = datetime.utcfromtimestamp(max_time)
            str_ago = time_ago(time_max)
            tabs.append([success("Latest Transaction"), success(str_ago)])

    if url is not None:
        url = success(url.strip('.local').upper())
    else:
        url = 'RPC Node Info'
    return_str = tabulate(tabs,
                          colalign=["left", "right"],
                          headers=["Bitcoin Core", url])

    if refresh is not None:
        return_str += f'\n\nLast Refresh: {success(time_ago(refresh))}'

    return (return_str)


def data_sync():
    # Displays a large sync status
    # under [MAIN][message_widget]
    try:
        synch_bar, perc_c = pickle_it('load', 'synch_status.pkl')
    except Exception:
        return None
    from node_warden import load_config
    config = load_config(quiet=True)
    ft_config = config['MAIN']
    font = ft_config.get('large_text_font')
    try:
        message = f'{round(perc_c, 2)}%'
    except Exception:
        return None
    # If a price is provided, it won't refresh
    custom_fig = pyfiglet.Figlet(font=font)
    return_fig = custom_fig.renderText(message)
    if round(perc_c, 2) < 99.95:
        return_fig = yellow(return_fig)
    else:
        return_fig = success(return_fig)
    return_fig += muted('\nBlockchain Sync Status\n')

    inside_umbrel = pickle_it('load', 'inside_umbrel.pkl')
    raspiblitz = pickle_it('load', 'raspiblitz_detected.pkl')

    if inside_umbrel is True:
        return_fig += success('Umbrel Node Running\n')

    if raspiblitz is True:
        return_fig += success('Raspiblitz Node Running\n')

    return (return_fig)


def data_services(use_cache=False):
    services_found = pickle_it('load', 'services_found.pkl')
    if services_found == 'file not found':
        return_txt = (
            warning(' [i] No Local Nodes found yet. Scanning network...'))
        return return_txt
    if services_found is None:
        return_txt = (warning(
            ' [i] No Nodes found on the local network.\nMake sure WARden is connected to the same local network as your node.'
        ))
        return return_txt

    tabs = []
    for service in services_found:
        tabs.append([service[0][0], service[1][1], service[0][1]])

    tabs = tabulate(tabs,
                    headers=["Host", "Service", "IP Address"],
                    colalign=["left", "left", "center"])

    t = success('Node Services Detected in your Local Network\n')
    t += '---------------------------------------------\n\n'
    t += tabs

    try:
        refresh = pickle_it('load', 'services_refresh.pkl')
        t += '\n\nLast Check: ' + success(time_ago(refresh))
    except Exception:
        pass

    return (t)


def main():
    arg = sys.argv[1]
    if arg == 'data_btc_rpc_info':
        print(data_btc_rpc_info())
    if arg == 'data_umbrel':
        print(data_umbrel())
    if arg == 'data_btc_price':
        print(data_btc_price(use_cache=False))
    if arg == 'data_tor':
        print(data_tor())
    if arg == 'data_login':
        print(data_login())
    if arg == 'data_mempool':
        print(data_mempool())
    if arg == 'data_sys':
        print(data_sys())
    if arg == 'data_logger':
        print(data_logger())
    if arg == 'data_random_satoshi':
        print(data_random_satoshi())
    if arg == 'data_large_price':
        print(data_large_price())
    if arg == 'data_large_block':
        print(data_large_block())
    if arg == 'data_sync':
        print(data_sync())
    if arg == 'data_whitepaper':
        data_whitepaper()
    if arg == 'data_services':
        print(data_services())
    if arg == 'data_specter':
        print(data_specter(use_cache=False))


# HELPERS ------------------------------------------
# Function to load and save data into pickles
def humanbytes(B):
    'Return the given bytes as a human friendly KB, MB, GB, or TB string'
    B = float(B)
    KB = float(1024)
    MB = float(KB**2)  # 1,048,576
    GB = float(KB**3)  # 1,073,741,824
    TB = float(KB**4)  # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B / TB)


def pickle_it(action='load', filename=None, data=None):
    home_path = os.path.dirname(os.path.abspath(__file__))
    filename = 'static/save/' + filename
    filename = os.path.join(home_path, filename)
    if action == 'load':
        try:
            with open(filename, 'rb') as handle:
                ld = pickle.load(handle)
                handle.close()
                return (ld)
        except Exception:
            return ("file not found")
    else:
        try:
            with open(filename, 'wb') as handle:
                pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
                handle.close()
                return ("saved")
        except Exception:
            return ("failed")


def tail(file, n=1, bs=1024):
    try:
        f = open(file)
        f.seek(0, 2)
        l = 1 - f.read(1).count('\n')
        B = f.tell()
        while n >= l and B > 0:
            block = min(bs, B)
            B -= block
            f.seek(B, 0)
            l += f.read(block).count('\n')
        f.seek(B, 0)
        l = min(l, n)
        lines = f.readlines()[-l:]
        f.close()
        return lines
    except Exception:
        return None


if __name__ == "__main__":
    main()
