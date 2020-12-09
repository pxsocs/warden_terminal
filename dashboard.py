import keyboard

from time import sleep, time
from ansi_management import (warning, success, error, info, clear_screen, bold)
from data import data_tor, data_btc_price
from dashing import HSplit, VSplit, Text, Log


def main_dashboard(config, tor):

    while True:

        ui = HSplit(
            VSplit(tor_widget(tor), btc_price_widget(), ssh_widget()),
            VSplit(Text('Hello World,\nthis is dashing.', border_color=10),
                   Log(title='Bitcoin Log', border_color=10)),
            title=info(
                f"WARden | Bitcoin Console | Press {bold('[Q]')} to quit"),
            color=10)

        log = ui.items[1].items[1]
        log.append("0 -----")

        ui.display()

        # Refresh page after n seconds
        try:
            refresh_time = int(config['MAIN']['refresh'])
        except Exception:
            refresh_time = 5
        sleep(refresh_time)


def tor_widget(tor):
    tor_string = data_tor(tor)
    return (Text(tor_string, border_color=10, title='Tor Status', color=7))


def btc_price_widget():
    return_widget = Log(title='₿ Powered by NGU Tech', color=7, border_color=7)
    return_widget = data_btc_price(return_widget)
    return (return_widget)


def ssh_widget():
    return_widget = Log(title='SSH Logins to this computer',
                        color=7,
                        border_color=7)
    ssh_data = f"Time / User / Success"
    return_widget.append(ssh_data)
    return (return_widget)
