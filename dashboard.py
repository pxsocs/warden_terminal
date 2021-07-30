import logging
import pickle
import emoji
import urwid
import subprocess
import ast
import gc
import os
import configparser
from contextlib import suppress
from datetime import datetime
from ansi_management import (time_ago, warning, success, error, info,
                             clear_screen, bold, yellow, muted, cleanfloat,
                             jformat, time_ago)
from data import (btc_price_data, data_tor, data_btc_price, data_login,
                  data_mempool, data_random_satoshi, data_large_price,
                  data_whitepaper, data_sys, pickle_it, data_logger,
                  data_large_block, data_large_message, data_btc_rpc_info,
                  data_sync, data_specter)
from dependencies.urwidhelper.urwidhelper import translate_text_for_urwid


def load_config():
    # Load Config
    basedir = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.join(basedir, 'config.ini')
    CONFIG = configparser.ConfigParser()
    CONFIG.read(config_file)
    return (CONFIG)


def toggle(config_var, value=None):
    basedir = os.path.abspath(os.path.dirname(__file__))
    config = load_config()
    getter = config['MAIN'].getboolean(config_var)
    if not value:
        getter = not getter
    else:
        getter = value
    config['MAIN'][config_var] = str(getter)
    config_file = os.path.join(basedir, 'config.ini')
    with open(config_file, 'w') as configfile:
        config.write(configfile)


def version():
    version_file = 'version.txt'
    # Get Version
    try:
        with open(version_file, 'r') as file:
            version = file.read().replace('\n', '')
            file.close()
    except Exception:
        version = 'unknown'
    return (version)


def main_dashboard(config, tor):
    def update_header(layout, message=None, message_type=None):

        # Create Header
        try:
            r_time = pickle_it('load', 'last_price_refresh.pkl')
        except Exception:
            r_time = warning("No recent data")
        try:
            r_time = time_ago(r_time)
        except Exception:
            r_time = warning("No recent data")

        upgrade_available = pickle_it('load', 'upgrade.pkl')
        restart = pickle_it('load', 'restart.pkl')
        msg_add = None
        if upgrade_available is True:
            msg_add = ' [UPGRADE AVAILABLE] '
        if restart is True:
            msg_add = ' [RESTART THE APP] '

        if msg_add is not None:
            txt = ' WARden Node Edition (Version: ' + version() + str(
                msg_add) + emoji.emojize(') | twitter :bird: @alphaazeta')
        else:
            txt = ' WARden Node Edition (Version: ' + version(
            ) + emoji.emojize(') | twitter :bird: @alphaazeta')

        btc = btc_price_data()

        if btc != 'loading...':
            try:
                btc_price = btc['RAW']['BTC']['USD']['PRICE']
            except Exception:
                btc_price = 0
        else:
            btc_price = 0

        if btc_price > 0:
            txt += ('  |  ' + f"BTC ${jformat(btc_price, 0)} " +
                    "  | Last Refresh " + r_time)

        if message:
            txt += ' | ' + message

        small_display = pickle_it('load', 'small_display.pkl')
        if small_display is True:
            txt = ("WARden Node Edition | " +
                   f"BTC ${jformat(btc_price, 0)} " + " | " + r_time)

        header_text = urwid.Text(txt, align='right')
        header = urwid.AttrMap(header_text, 'titlebar')
        layout.header = header

    def refresh_menu(layout):
        config = load_config()

        audio = config['MAIN']['sound']
        auto_scroll = config['MAIN'].getboolean('auto_scroll')
        multi = pickle_it('load', 'multi_toggle.pkl')
        audio_str = "ON" if audio is True else "OFF"
        multi_str = "ON" if multi is True else "OFF"

        lst_menu = []
        small_display = pickle_it('load', 'small_display.pkl')
        if small_display:
            lst_menu.append(['Use arrows to cycle screens |  '])
            lst_menu.append([f'(S) Auto Scroll [{auto_scroll}]  |  '])
        lst_menu.append([f'(A) Audio on/off [{audio_str}] |  '])
        lst_menu.append(['(H) to toggle private info  |  '])
        lst_menu.append(['(D) Download Bitcoin Whitepaper (bitcoin.pdf)  |  '])

        lst_menu.append([f'(M) to toggle multi view [{multi_str}] |  '])
        lst_menu.append(['(Q) to quit'])
        small_display = pickle_it('load', 'small_display.pkl')
        if small_display is True:
            layout.footer = None
            return None
        else:
            menu = urwid.Text(lst_menu, align='center')
            layout.footer = menu
            return (menu)

    # Class to Create URWID box window to receive data
    class Box:
        def __init__(self,
                     loader_text=None,
                     valign='top',
                     top=1,
                     bottom=1,
                     left=1,
                     right=1,
                     height=None,
                     text_align='left'):
            self.loader_text = loader_text
            self.valign = valign
            self.top = top
            self.bottom = bottom
            self.left = left
            self.right = right
            self.height = height
            self.text_align = text_align
            self.text = urwid.Text(self.loader_text, align=self.text_align)
            self.filler = urwid.Filler(self.text,
                                       valign=self.valign,
                                       top=self.top,
                                       bottom=self.bottom)
            self.v_padding = urwid.Padding(self.filler,
                                           left=self.left,
                                           right=self.right)
            self.line_box = urwid.LineBox(self.v_padding)
            self.box_size = self.height

    palette = [('titlebar', 'dark green', ''),
               ('refresh button', 'dark green,bold', ''),
               ('quit button', 'dark green', ''), ('button', 'dark blue', ''),
               ('getting quote', 'dark blue', ''),
               ('headers', 'white,bold', ''), ('change ', 'dark green', ''),
               ('change negative', 'dark red', '')]

    # Create the BTC price box

    quote_box = Box(loader_text='Loading Prices...').line_box

    large_message = Box(loader_text='Loading...',
                        height=12,
                        text_align='center',
                        valign='middle',
                        top=3).line_box

    large_message.base_widget.set_text(
        translate_text_for_urwid(data_large_message()))

    large_block = Box(loader_text='Getting Block Height...',
                      height=12,
                      text_align='center',
                      valign='middle',
                      top=3).line_box

    sync_block = Box(loader_text='Checking Node Sync...',
                     height=12,
                     text_align='center',
                     valign='middle',
                     top=3).line_box

    moscow_time_block = Box(loader_text='Getting Block Height...',
                            height=12,
                            text_align='center',
                            valign='middle',
                            top=3).line_box

    large_price = Box(loader_text='Getting BTC Price...',
                      height=12,
                      text_align='center',
                      valign='middle',
                      top=3).line_box

    rpc_box = Box(loader_text='Getting Bitcoin Core Info [RPC]...').line_box

    specter_box = Box(loader_text='Connecting to Specter Server...',
                      height=12,
                      text_align='center',
                      valign='middle',
                      top=3).line_box

    # Create the Large Price Box
    tor_box_size = 10
    tor_box = Box(loader_text='Checking Tor Status...',
                  height=tor_box_size).line_box

    # Create user login Box
    login_box_size = 12
    login_box = Box(loader_text='Loading User Logins...',
                    height=login_box_size).line_box

    # Create MemPool Box
    mp_box_size = 24
    mp_box = Box(loader_text='Loading Mempool...', height=mp_box_size).line_box

    # Create SysInfo Box
    sys_box_size = 24
    sys_box = Box(loader_text='Loading System Info...',
                  height=sys_box_size).line_box

    # Create Logger Box
    logger_box_size = 20
    logger_box = Box(loader_text='Loading Message Log...',
                     height=logger_box_size).line_box

    # Create the Satoshi Quotes Box
    satoshi_box_size = 20
    satoshi_box = Box(loader_text='Loading Satoshi Wisdom...',
                      height=satoshi_box_size).line_box

    # Assemble the widgets
    header = 'Loading...'

    log_tor = urwid.Columns(
        [sys_box, urwid.Pile([login_box, tor_box]), mp_box])
    bottom_box = urwid.Columns([logger_box, satoshi_box])

    try:
        rpc_running = pickle_it('load', 'rpc_running.pkl')
    except Exception:
        rpc_running = False

    if rpc_running is True:
        top_box = urwid.Columns([quote_box, rpc_box, large_price])
    else:
        top_box = urwid.Columns([quote_box, large_price])

    body_widget = urwid.Pile([top_box, log_tor, bottom_box])

    widget_list = [
        large_price, quote_box, mp_box, tor_box, logger_box, satoshi_box,
        sys_box, large_block, large_message, moscow_time_block
    ]

    if rpc_running is True:
        widget_list.append(rpc_box)
        widget_list.append(sync_block)

    specter_ip = pickle_it('load', 'specter_ip.pkl')
    if specter_ip is not None:
        widget_list.append(specter_box)

    try:
        small_display = pickle_it('load', 'small_display.pkl')
        multi = pickle_it('load', 'multi_toggle.pkl')
        if multi is True:
            small_display = False

    except Exception:
        small_display = False

    cycle = pickle_it('load', 'cycle.pkl')

    if not isinstance(cycle, int):
        cycle = 0

    if not small_display:
        layout = urwid.Frame(header=header,
                             body=body_widget,
                             footer='Loading...')
    else:
        layout = urwid.Frame(header=header,
                             body=widget_list[cycle],
                             footer='Loading...')

    refresh_menu(layout)

    # Handle key presses
    def handle_input(key):
        if key == 'Q' or key == 'q':
            raise urwid.ExitMainLoop()
        if key == 'A' or key == 'a':
            toggle('sound')
        if key == 'H' or key == 'h':
            toggle('hide_private_info')
            tor_box.base_widget.set_text("Updating... Please Wait.")
        if key == 'D' or key == 'd':
            logger_box.base_widget.set_text(data_whitepaper())
        if key == 'right' or key == 'down':
            small_display = pickle_it('load', 'small_display.pkl')
            if small_display:
                cycle = pickle_it('load', 'cycle.pkl')
                cycle += 1
                if cycle > (len(widget_list) - 1):
                    cycle = 0
                pickle_it('save', 'cycle.pkl', cycle)
                layout.body = widget_list[cycle]
        if key == 'left' or key == 'down':
            small_display = pickle_it('load', 'small_display.pkl')
            if small_display:
                cycle = pickle_it('load', 'cycle.pkl')
                cycle -= 1
                if cycle < 0:
                    cycle = (len(widget_list) - 1)
                pickle_it('save', 'cycle.pkl', cycle)
                layout.body = widget_list[cycle]

        # Toggle multi windows / gadgets or single
        if key == 'M' or key == 'm':
            try:
                multi = pickle_it('load', 'multi_toggle.pkl')
            except Exception:
                multi = True
            # toggle
            multi = not multi
            pickle_it('save', 'multi_toggle.pkl', multi)
            # Turn off auto scroll on multi gadget display
            if multi is True:
                toggle('auto_scroll', False)

        if key == 'S' or key == 's':
            toggle('auto_scroll')
            refresh_menu(layout)

        else:
            pass

        refresh_menu(layout)
        main_loop.draw_screen()

    def check_for_pump(_loop, _data):
        try:
            btc = pickle_it('load', 'btc_price_data.pkl')
            btc_price = btc['DISPLAY']['BTC']['USD']['PRICE']
            chg_str = btc['DISPLAY']['BTC']['USD']['CHANGEPCTDAY']
            chg = cleanfloat(chg_str)
            if chg > 5:
                logging.info(
                    info("[NgU] ") + muted("Looks like Bitcoin is pumping ") +
                    yellow(f' {btc_price}') + success(f' +{chg_str}%'))
            if chg < -5:
                logging.info(
                    info("[NgU] ") + muted(
                        "Looks like Bitcoin is dropping. Time to stack some sats. "
                    ) + yellow(f' {btc_price}') + error(f' {chg_str}%'))
        except Exception:
            pass

        main_loop.set_alarm_in(1, check_for_pump)

    def get_quote(_loop, _data):
        quote = translate_text_for_urwid(data_random_satoshi())
        satoshi_box.base_widget.set_text(quote)
        main_loop.set_alarm_in(120, get_quote)

    def rpc_updater(_loop, __data):
        data = translate_text_for_urwid(data_btc_rpc_info())
        rpc_box.base_widget.set_text(data)
        main_loop.set_alarm_in(1, rpc_updater)

    def sync_updater(_loop, __data):
        try:
            data = translate_text_for_urwid(data_sync())
            sync_block.base_widget.set_text(data)
        except Exception:
            pass
        main_loop.set_alarm_in(1, sync_updater)

    def large_block_updater(_loop, __data):
        data = translate_text_for_urwid(data_large_block())
        large_block.base_widget.set_text(data)
        main_loop.set_alarm_in(1, large_block_updater)

    def btc_updater(_loop, __data):
        data = translate_text_for_urwid(data_btc_price())
        quote_box.base_widget.set_text(data)

        data = translate_text_for_urwid(data_large_price())
        large_price.base_widget.set_text(data)

        data = translate_text_for_urwid(data_large_price(moscow_time=True))
        moscow_time_block.base_widget.set_text(data)

        update_header(layout)
        main_loop.draw_screen()
        main_loop.set_alarm_in(1, btc_updater)

    def tor_updater(_loop, __data):
        try:
            data = translate_text_for_urwid(data_tor())
        except Exception:
            pass
        tor_box.base_widget.set_text(data)
        main_loop.set_alarm_in(1, tor_updater)

    def login_updater(_loop, __data):
        data = translate_text_for_urwid(data_login())
        login_box.base_widget.set_text(data)
        main_loop.set_alarm_in(1, login_updater)

    def logger_updater(_loop, __data):
        data = translate_text_for_urwid(data_logger())
        logger_box.base_widget.set_text(data)
        main_loop.set_alarm_in(1, logger_updater)

    def mp_updater(_loop, __data):
        data = translate_text_for_urwid(data_mempool())
        mp_box.base_widget.set_text(data)
        main_loop.set_alarm_in(1, mp_updater)

    def specter_updater(_loop, __data):
        data = translate_text_for_urwid(data_specter())
        specter_box.base_widget.set_text(data)
        main_loop.set_alarm_in(1, specter_updater)

    def sys_updater(_loop, __data):
        data = translate_text_for_urwid(data_sys())
        sys_box.base_widget.set_text(data)
        main_loop.set_alarm_in(1, sys_updater)

    def check_screen_size(_loop, __data):
        try:
            rows, columns = subprocess.check_output(['stty', 'size'],
                                                    close_fds=True).split()
        except OSError:
            return

        rows = int(rows)
        columns = int(columns)

        # min dimensions are recommended at 60 x 172
        if rows < 60 or columns < 172:
            multi = pickle_it('load', 'multi_toggle.pkl')
            if multi is False:
                small_display = True
            else:
                small_display = False
            pickle_it('save', 'small_display.pkl', small_display)
        else:
            small_display = False
            pickle_it('save', 'small_display.pkl', small_display)

        main_loop.set_alarm_in(1, check_screen_size)

    def refresh(_loop, _data):
        config = load_config()
        auto_scroll = config['MAIN'].getboolean('auto_scroll')
        if auto_scroll:
            cycle = pickle_it('load', 'cycle.pkl')
            small_display = pickle_it('load', 'small_display.pkl')
            if small_display:
                layout.body = widget_list[cycle]
                cycle += 1
                if cycle > (len(widget_list) - 1):
                    cycle = 0
                pickle_it('save', 'cycle.pkl', cycle)
            else:
                layout.body = body_widget

            small_display = pickle_it('load', 'small_display.pkl')
            if small_display:
                layout.body = widget_list[cycle]

        # Will wait 5 seconds per screen beforing cycling
        refresh_time = config['MAIN'].getint('refresh')
        main_loop.set_alarm_in(refresh_time, refresh)

    main_loop = urwid.MainLoop(layout, palette, unhandled_input=handle_input)
    main_loop.set_alarm_in(0, refresh)
    main_loop.set_alarm_in(0, check_for_pump)
    main_loop.set_alarm_in(0, large_block_updater)
    main_loop.set_alarm_in(0, specter_updater)
    main_loop.set_alarm_in(0, sync_updater)
    main_loop.set_alarm_in(0, btc_updater)
    main_loop.set_alarm_in(0, sys_updater)
    main_loop.set_alarm_in(0, rpc_updater)
    main_loop.set_alarm_in(0, logger_updater)
    main_loop.set_alarm_in(0, login_updater)
    main_loop.set_alarm_in(0, tor_updater)
    main_loop.set_alarm_in(0, mp_updater)
    main_loop.set_alarm_in(0, get_quote)
    main_loop.set_alarm_in(0, check_screen_size)
    main_loop.run()
