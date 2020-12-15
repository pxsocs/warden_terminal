import logging
import emoji
import urwid
import subprocess
import ast
import gc
import pyttsx3
from datetime import datetime
from ansi_management import (warning, success, error, info, clear_screen, bold,
                             yellow, muted, cleanfloat)
from data import (btc_price_data, data_tor, data_btc_price, data_login,
                  data_mempool, data_random_satoshi, data_large_price)
from dependencies.urwidhelper.urwidhelper import translate_text_for_urwid


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

    try:
        refresh_interval = int(config['MAIN'].get('refresh'))
    except Exception:
        refresh_interval = 5

    running_jobs = {
        'btc': {
            'workers': 0
        },
        'tor': {
            'workers': 0
        },
        'login': {
            'workers': 0
        },
        'mp': {
            'workers': 0
        },
        'logger': {
            'workers': 0
        },
        'large_price': {
            'workers': 0
        }
    }

    palette = [('titlebar', 'dark green', ''),
               ('refresh button', 'dark green,bold', ''),
               ('quit button', 'dark green', ''),
               ('getting quote', 'dark blue', ''),
               ('headers', 'white,bold', ''), ('change ', 'dark green', ''),
               ('change negative', 'dark red', '')]

    def exit_on_q(key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def update_header(layout, message=None, message_type=None):
        # Create Header
        refresh_time = datetime.now().strftime('%H:%M:%S')
        txt = u' WARden Node Edition (Version: ' + version() + emoji.emojize(
            ') | twitter :bird: @alphaazeta | Last Refresh on: '
        ) + refresh_time
        if message:
            txt += ' | ' + message
        header_text = urwid.Text(txt, align='right')
        header = urwid.AttrMap(header_text, 'titlebar')
        layout.header = header

    # Draw empty dashboard
    menu = urwid.Text([u'Press (', ('quit button', u'Q'), u') to quit.'])

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

    # Create the BTC price box
    quote_box_size = len(ast.literal_eval(
        config['CURRENCIES'].get('fx_list'))) + 10
    quote_box = Box(loader_text='Loading Prices...',
                    height=quote_box_size).line_box

    # Create the TOR Box
    large_price_size = quote_box_size
    large_price = Box(loader_text='Getting BTC Price...',
                      height=large_price_size,
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

    # Create Logger Box
    logger_box_size = 10
    logger_box = Box(loader_text='Loading Message Log...',
                     height=logger_box_size).line_box

    # Create the Satoshi Quotes Box
    satoshi_box_size = 20
    satoshi_box = Box(loader_text='Loading Satoshi Wisdom...',
                      height=satoshi_box_size).line_box

    # Assemble the widgets
    header = 'Loading...'
    log_tor = urwid.Columns([mp_box, urwid.Pile([login_box, tor_box])])
    log_tor_size = max(mp_box_size, login_box_size, tor_box_size)
    bottom_box_size = max(satoshi_box_size, logger_box_size)
    bottom_box = urwid.Columns([logger_box, satoshi_box])
    top_box = urwid.Columns([quote_box, large_price])
    top_box_size = max(large_price_size, quote_box_size)
    body_widget = urwid.Pile([(top_box_size, top_box), (log_tor_size, log_tor),
                              (bottom_box_size, bottom_box)])

    layout = urwid.Frame(header=header, body=body_widget, footer=menu)
    update_header(layout)

    # Handle key presses
    def handle_input(key):
        if key == 'Q' or key == 'q':
            raise urwid.ExitMainLoop()

        else:
            pass

    def check_for_pump(_loop, _data):
        try:
            btc = btc_price_data()
            btc_price = btc['DISPLAY']['BTC']['USD']['PRICE']
            chg_str = btc['DISPLAY']['BTC']['USD']['CHANGEPCTDAY']
            chg = cleanfloat(chg_str)
            if chg > 5:
                logging.info(
                    info("[NGU] ") + muted(f"Looks like Bitcoin is pumping ") +
                    emoji.emojize(":rocket:") + yellow(f' {btc_price}') +
                    success(f' +{chg_str}%'))
            if chg < -5:
                logging.info(
                    info("[NGU] ") + muted(
                        f"Looks like Bitcoin is dropping. Time to stack some sats. "
                    ) + yellow(f' {btc_price}') + error(f' {chg_str}%'))
        except Exception:
            pass

        main_loop.set_alarm_in(300, check_for_pump)

    def get_quote(_loop, _data):
        quote = translate_text_for_urwid(data_random_satoshi())
        satoshi_box.base_widget.set_text(quote)
        main_loop.set_alarm_in(120, get_quote)

    def refresh(_loop, _data):
        # Add Background Tasks
        update_header(layout)
        main_loop.draw_screen()

        # Add Background Updates
        # UPDATER FUNCTIONS - ONE NEEDED PER UPDATE
        # These run on background as watch pipes
        def update_btc(read_data):
            read_data = translate_text_for_urwid(read_data)
            quote_box.base_widget.set_text(read_data)
            main_loop.remove_watch_pipe = True
            running_jobs['btc']['workers'] = 0
            for pipe in running_jobs['btc']['pipe']:
                if pipe != []:
                    pipe.kill()
                    gc.collect()

        def update_tor(read_data):
            read_data = translate_text_for_urwid(read_data)
            tor_box.base_widget.set_text(read_data)
            running_jobs['tor']['workers'] = 0
            for pipe in running_jobs['tor']['pipe']:
                if pipe != []:
                    pipe.kill()
                    gc.collect()

        def update_large_price(read_data):
            read_data = translate_text_for_urwid(read_data)
            large_price.base_widget.set_text(read_data)
            running_jobs['large_price']['workers'] = 0
            for pipe in running_jobs['large_price']['pipe']:
                if pipe != []:
                    pipe.kill()
                    gc.collect()

        def update_login(read_data):
            read_data = translate_text_for_urwid(read_data)
            login_box.base_widget.set_text(read_data)
            running_jobs['login']['workers'] = 0
            for pipe in running_jobs['login']['pipe']:
                if pipe != []:
                    pipe.kill()
                    gc.collect()

        def update_mp(read_data):
            read_data = translate_text_for_urwid(read_data)
            mp_box.base_widget.set_text(read_data)
            main_loop.remove_watch_pipe = True
            running_jobs['mp']['workers'] = 0
            for pipe in running_jobs['mp']['pipe']:
                if pipe != []:
                    pipe.kill()
                    gc.collect()

        def update_logger(read_data):
            read_data = translate_text_for_urwid(read_data)
            logger_box.base_widget.set_text(read_data)
            main_loop.remove_watch_pipe = True
            running_jobs['logger']['workers'] = 0
            for pipe in running_jobs['logger']['pipe']:
                if pipe != []:
                    pipe.kill()
                    gc.collect()

        # Job List Dictionaty
        job_list = {
            'btc': {
                'max_workers': 1,
                'subprocess': 'python3 data.py data_btc_price',
                'updater': update_btc
            },
            'tor': {
                'max_workers': 1,
                'subprocess': 'python3 data.py data_tor',
                'updater': update_tor
            },
            'login': {
                'max_workers': 1,
                'subprocess': 'python3 data.py data_login',
                'updater': update_login
            },
            'mp': {
                'max_workers': 1,
                'subprocess': 'python3 data.py data_mempool',
                'updater': update_mp
            },
            'logger': {
                'max_workers': 1,
                'subprocess': 'python3 data.py data_logger',
                'updater': update_logger
            },
            'large_price': {
                'max_workers': 1,
                'subprocess': 'python3 data.py data_large_price',
                'updater': update_large_price
            }
        }

        for job in job_list.keys():
            if running_jobs[job]['workers'] < job_list[job]['max_workers']:
                running_jobs[job]['workers'] += 1
                stdout = main_loop.watch_pipe(job_list[job]['updater'])
                stderr = main_loop.watch_pipe(job_list[job]['updater'])
                launch_process = subprocess.Popen(job_list[job]['subprocess'],
                                                  shell=True,
                                                  stdout=stdout,
                                                  stderr=stderr)
                # Store or create a list to store
                running_jobs[job].setdefault('pipe', []).append(launch_process)

        main_loop.set_alarm_in(refresh_interval, refresh)

    try:
        main_loop = urwid.MainLoop(layout,
                                   palette,
                                   unhandled_input=handle_input)
        main_loop.set_alarm_in(30, check_for_pump)
        main_loop.set_alarm_in(10, get_quote)
        main_loop.set_alarm_in(0, refresh)
        main_loop.run()
    except Exception as e:  # Catch some timeouts - only once
        logging.error(info('[MAIN] ') + muted('Error: ') + yellow(str(e)))
        update_header(layout, message=f'Error: {e}')
        main_loop = urwid.MainLoop(layout,
                                   palette,
                                   unhandled_input=handle_input)
        main_loop.run()
