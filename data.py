import ast
import sys
import subprocess
import emoji
from tabulate import tabulate

from datetime import datetime, timedelta
from dateutil import parser

from connections import test_tor, tor_request
from ansi_management import (warning, success, error, info, clear_screen, bold,
                             jformat, muted, time_ago)

from pricing_engine import multiple_price_grab


def data_tor(tor=None):
    if not tor:
        tor = test_tor()

    tor_string = f"""
 Tor  IP Address {tor['post_proxy']['origin']}
 Ping Time {tor['post_proxy_ping']}
 {success("Running on port")} {info(bold(tor['port']))}
 Real IP Address {muted(tor['pre_proxy']['origin'])}
 Ping Time {muted(tor['pre_proxy_ping'])}"""
    return (tor_string)


def data_login():
    tabs = []
    processes = subprocess.check_output("last")
    processes = list(processes.splitlines())
    for process in processes:
        try:
            process = process.decode("utf-8")
            if 'still logged in' not in process:
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
    tabs = tabulate(tabs,
                    headers=['Users Logged in to this computer'],
                    colalign=["left"])

    return (tabs)


def data_btc_price():
    from node_warden import load_config
    config = load_config(quiet=True)
    fx_config = config['CURRENCIES']
    currencies = ast.literal_eval(fx_config.get('fx_list'))
    primary_fx = ast.literal_eval(fx_config.get('primary_fx'))
    price_data = multiple_price_grab('BTC', ','.join(currencies))

    # Get prices in different currencies
    tabs = []
    for fx in currencies:
        try:
            price_str = price_data['DISPLAY']['BTC'][fx]['PRICE']
            chg_str = price_data['DISPLAY']['BTC'][fx]['CHANGEPCTDAY']
            high = price_data['DISPLAY']['BTC'][fx]['HIGHDAY']
            low = price_data['DISPLAY']['BTC'][fx]['LOWDAY']
            market = muted(price_data['DISPLAY']['BTC'][fx]['LASTMARKET'])
            try:
                chg = float(chg_str)
                if chg > 0:
                    chg_str = success(chg_str + ' %')
                elif chg < 0:
                    chg_str = error(chg_str + ' %')
            except Exception:
                chg_str = muted(chg_str + ' %')

            if fx == primary_fx:
                fx = info(fx)
            tabs.append(
                [u'  ' + fx, price_str, chg_str, low + ' - ' + high, market])

        except Exception as e:
            tabs.append(['error: ' + str(e)])

    tabs = tabulate(
        tabs,
        headers=['Fiat', 'Price', '% change', '24h Range', 'Source'],
        colalign=["center", "right", "right", "center", "right"])

    tabs += (
        f"\n\n Last Refresh on: {info(datetime.now().strftime('%H:%M:%S'))}")
    return tabs


def data_mempool():
    from node_warden import load_config
    config = load_config(quiet=True)
    mp_config = config['MEMPOOL']
    url = mp_config.get('url')
    tabs = []

    # Get recommended fees

    mp_fee = tor_request(url + '/api/v1/fees/recommended').json()
    tabs = list(mp_fee.values())
    tabs = [[str(x) + ' sats/Vb' for x in tabs]]
    tabs = tabulate(tabs,
                    headers=["Fastest Fee", "30 min fee", "1 hour fee"],
                    colalign=["center", "center", "center"])
    block_height = tor_request(url + '/api/blocks/tip/height').json()
    block_txt = success(f' Block Height: {block_height}\n\n')
    tabs = block_txt + info(' Mempool Fee Estimates: \n') + tabs

    mp_blocks = tor_request(url + '/api/blocks').json()

    mp_tabs = []
    for block in mp_blocks:
        mp_tabs.append([
            time_ago(block['timestamp']),
            jformat(block['height'], 0),
            jformat(block['tx_count'], 0),
            jformat(block['size'], 2, 1000000) + ' MB'
        ])

    mp_tabs = tabulate(mp_tabs,
                       headers=[" Time", "Height", "Tx Count", "Size"],
                       colalign=["right", "center", "center", "right"])
    tabs += info('\n\n Latest Blocks: \n') + mp_tabs
    tabs += muted(f"\n\n Source: {url}  {success('[Tor Request]')}\n")
    return tabs


def main():
    arg = sys.argv[1]
    if arg == 'data_btc_price':
        print(data_btc_price())
    if arg == 'data_tor':
        print(data_tor())
    if arg == 'data_login':
        print(data_login())
    if arg == 'data_mempool':
        print(data_mempool())


if __name__ == "__main__":
    main()