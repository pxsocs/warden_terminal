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

    🛰  Tor  IP Address {tor['post_proxy']['origin']}
       Ping Time {tor['post_proxy_ping']}

    🛰  Real IP Address {tor['pre_proxy']['origin']}
       Ping Time {tor['pre_proxy_ping']}

        """
    return (tor_string)


def data_ssh():
    # SSH Logs Files
    # Ubuntu:
    # /var/log/auth.log
    # RedHat:
    # /var/log/secure
    # Note that the default configuration on Ubuntu is to NOT log ssh logins to the /var/log/auth file. This is the INFO logging level.

    # If you want to have it include login attempts in the log file, you'll need to edit the /etc/ssh/sshd_config file (as root or with sudo) and change the LogLevel from INFO to VERBOSE.

    # After that, restart the sshd daemon with

    # sudo service rsyslog restart
    # After that, the ssh login attempts will be logged into the /var/log/auth.log file.
    pass


def data_btc_price(return_widget):
    from node_warden import load_config
    config = load_config(quiet=True)
    updt = muted(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
    return_widget.append(f"    ₿ Realtime Prices ({updt})")
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
                return_widget.append(f"    {price} {fx_details['symbol']}")
            except Exception as e:
                print(e)
                return_widget.append(f'Error on reatime data for {fx}: {e}')
        else:
            return_widget.append(f'{fx} is not a currency')

    return return_widget
