import subprocess
from datetime import datetime
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
    try:
        processes = subprocess.check_output("who")
        users = list(
            [x.split()[0].decode("utf-8") for x in processes.splitlines()])
        console = list(
            [x.split()[1].decode("utf-8") for x in processes.splitlines()])
        log_month = list(
            [x.split()[2].decode("utf-8") for x in processes.splitlines()])
        log_day = list(
            [x.split()[3].decode("utf-8") for x in processes.splitlines()])
        log_time = list(
            [x.split()[4].decode("utf-8") for x in processes.splitlines()])

        count = 0
        return_widget.append("")
        for element in users:
            return_widget.append(
                f"   {warning(users[count])} at {console[count]} logged on {success(log_time[count])} {success(log_month[count])}-{success(log_day[count])}"
            )
            count += 1
    except Exception as e:
        return_widget.append(f"  Error getting User Log data: {e} ")

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
        if is_currency(fx):
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
