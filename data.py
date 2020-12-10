import subprocess
import emoji
from datetime import datetime, timedelta
from dateutil import parser

from connections import test_tor
from ansi_management import (warning, success, error, info, clear_screen, bold,
                             jformat, muted)

from pricing_engine import fx_rate, price_data_rt, is_currency


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
    processes = subprocess.check_output("who")
    processes = list(processes.splitlines())
    for process in processes:
        # try:
        process = process.decode("utf-8")
        user = process.split()[0]
        process = process.replace(user, '')
        console = process.split()[0]
        process = process.replace(console, '')
        date_str = parser.parse(process)
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
            f"   {warning(user)} at {muted(console)} " +
            bold(f"logged on {success(date_str.strftime('%H:%M (%b-%d)' ))}"))
        # except Exception as e:
        #     return_widget.append(f"  {process}")
        #     return_widget.append(f"  {e}")

    return (return_widget)


def data_btc_price(return_widget):
    from node_warden import load_config
    config = load_config(quiet=True)
    updt = muted(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
    return_widget.append("")
    return_widget.title = f"   ₿ Realtime Prices ({updt})"
    currencies = config.items("CURRENCIES")

    # Get prices in different currencies
    for key, fx in currencies:
        if fx == 'GBTC':
            price = jformat(price_data_rt("GBTC"), 2)
            return_widget.append(f"GBTC:   ${price}")
        elif is_currency(fx):
            try:
                fx_details = fx_rate(fx)
                fx_r = {
                    'cross': fx_details['symbol'],
                    'fx_rate': fx_details['fx_rate']
                }
                fx_r['btc_usd'] = price_data_rt("BTC")
                fx_r['btc_fx'] = fx_r['btc_usd'] * fx_r['fx_rate']
                price = jformat(fx_r['btc_fx'], 2)
                return_widget.append(f"   {price} {fx_details['symbol']}")
            except Exception as e:
                print(e)
                return_widget.append(f'Error on reatime data for {fx}: {e}')
        else:
            return_widget.append(f'{fx} is not a currency')

    return_widget.append(warning("   ₿ Powered by NGU Tech"))

    return return_widget
