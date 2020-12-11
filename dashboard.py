import keyboard

from time import sleep, time
from ansi_management import (warning, success, error, info, clear_screen, bold)
from data import data_tor, data_btc_price, data_login
from dashing import HSplit, VSplit, Text, Log


def main_dashboard(config, tor, spinner):

    while True:

        ui = HSplit(
            VSplit(btc_price_widget(), tor_widget(tor), ssh_widget()),
            VSplit(Text('Hello World,\nthis is dashing.', border_color=10),
                   Log(title='Bitcoin Log', border_color=10)),
            title=info(
                f"WARden | Bitcoin Console | Press {bold('[Q]')} to quit"),
            color=10)

        ui.display()

        # Refresh page after n seconds
        try:
            refresh_time = int(config['MAIN']['refresh'])
        except Exception:
            refresh_time = 1
        sleep(refresh_time)


def tor_widget(tor):
    tor_string = data_tor(tor)
    return (Text(tor_string, border_color=10, title='Tor Status', color=7))


def btc_price_widget():
    return_widget = data_btc_price()
    return (return_widget)


def ssh_widget():
    return_widget = Log(title='Users Currently Logged in',
                        color=7,
                        border_color=7)
    return_widget = data_login(return_widget)
    return (return_widget)
