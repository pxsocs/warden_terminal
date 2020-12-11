import ast
import subprocess
import emoji
import dashing

from datetime import datetime, timedelta
from dateutil import parser

from connections import test_tor
from ansi_management import (warning, success, error, info, clear_screen, bold,
                             jformat, muted)

from pricing_engine import multiple_price_grab


def data_tor(tor=None):
    if not tor:
        tor = test_tor()

    tor_string = f"""
   {success("Running on port")} {info(bold(tor['port']))}

   Tor  IP Address {tor['post_proxy']['origin']}
   Ping Time {tor['post_proxy_ping']}

   Real IP Address {tor['pre_proxy']['origin']}
   Ping Time {tor['pre_proxy_ping']}

        """
    return (tor_string)


def data_login(return_widget):

    return_widget.append("")
    processes = subprocess.check_output("last")
    processes = list(processes.splitlines())
    for process in processes:
        try:
            process = process.decode("utf-8")
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
                return_widget.append(
                    error(
                        f" {warn} {error(f'User Recently Logged in (last {expiration} min)')}:"
                    ))
            return_widget.append(
                f"   {warning(user)} at {muted(console)} " + bold(
                    f"logged on {success(date_str.strftime('%H:%M (%b-%d)' ))}"
                ))
        except Exception as e:
            return_widget.append(f"  {process}")
            return_widget.append(f"  {e}")

    return (return_widget)


def data_btc_price():
    return_widget = []
    from node_warden import load_config
    config = load_config(quiet=True)
    updt = muted(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
    return_widget.append("")
    currencies = ast.literal_eval(config.items("CURRENCIES")[0][1])

    price_data = multiple_price_grab('BTC', ','.join(currencies))

    # Get prices in different currencies
    for fx in currencies:
        try:
            price_str = price_data['DISPLAY']['BTC'][fx]['PRICE']
            return_widget.append(f"   {price_str}")
        except Exception as e:
            return_widget.append(f'Error on realtime data for {fx}: {e}')

    return_widget = '\n'.join(return_widget)

    return_widget = dashing.Text(return_widget,
                                 title=f'   ₿ Realtime Prices ({updt})  ',
                                 color=7,
                                 border_color=7)

    return return_widget
