import jinja2
from datetime import datetime
from node_warden import pickle_it
from flask import (Blueprint, render_template, url_for, jsonify, request,
                   redirect, Response)

warden = Blueprint('warden', __name__)


# Welcome Page
@warden.route("/", methods=['GET'])
def warden_page():
    first_time = pickle_it('load', 'first_time.pkl')
    if first_time == 'file not found':
        pickle_it('save', 'first_time.pkl', False)
        return render_template("warden/welcome.html",
                               title="Welcome to the WARden")
    else:
        return redirect(url_for("warden.terminal"))


@warden.route("/terminal", methods=['GET'])
def terminal():
    # # Get data to send to page - this data is being updated in background
    # # and saved on pickle files locally, so a page refresh will get the latest data
    # load_files = [
    #     'tor', 'app', 'block', 'btc_network', 'btcrpc_refresh', 'hosts_found',
    #     'last_price_refresh', 'recent_block', 'services_found', 'upgrade',
    #     'webserver', 'multi_price', 'services_refresh'
    # ]

    return render_template("warden/terminal.html",
                           title="Terminal View",
                           current_app=pickle_it('load', 'app.pkl'))


@warden.route("/settings", methods=['GET'])
def settings():
    from routes.forms import Settings
    form = Settings()
    return render_template("warden/settings.html", title="Settings", form=form)


# Main Method to display Pickle Files in real time
# usage: /broadcast?data=block
@warden.route("/broadcast", methods=['GET'])
def broadcast():
    from node_warden import pickle_it
    file = request.args.get("data")
    if file is None:
        return 'file not found'

    broadcaster = pickle_it('load', file + '.pkl')

    ansi_conv = request.args.get("ansi_to_html")
    if ansi_conv is not None:
        from ansi_management import ansi_to_html
        broadcaster = ansi_to_html(broadcaster)
        return broadcaster

    return jsonify(broadcaster)


@warden.route("/widget_broadcast", methods=['GET'])
def widget_broadcast():
    from node_warden import pickle_it
    current_widget = pickle_it('load', 'current_widget.pkl')
    if current_widget == 'multiwidget':
        current_widget = 'large_price'

    function_finder = {
        "large_price": 'data_large_price',
        'quote_box': 'data_btc_price',
        'mp_box': 'data_mempool',
        'tor_box': 'data_tor',
        'logger_box': 'data_logger',
        'satoshi_box': 'data_satoshi',
        'sys_box': 'data_sys',
        'large_block': 'data_large_block',
        'large_message': 'data_large_message',
        'moscow_time_block': 'data_moscow_time',
        'services_box': 'data_services',
        'webserver_box': 'webserver',
        'sync_block': 'data_sync',
        'rpc_box': 'data_rpc',
        'specter_box': 'da_specter'
    }

    try:
        broadcaster = pickle_it('load',
                                function_finder[current_widget] + '.pkl')
    except Exception as e:
        broadcaster = f'{current_widget} Error : {e}'

    from ansi_management import ansi_to_html
    broadcaster = ansi_to_html(broadcaster)
    return broadcaster


@warden.route("/get_widget", methods=['GET'])
def get_widget():
    from dashboard_elements import progress_bar
    pb = progress_bar('Test it', 20, 100, 0, True, True, 'bg-danger')
    return pb


# -------------------------------------------------
#  START JINJA 2 Filters
# -------------------------------------------------
# Jinja2 filter to format time to a nice string
# Formating function, takes self +
# number of decimal places + a divisor


@jinja2.contextfilter
@warden.app_template_filter()
def sensitive(context, txt):
    from node_warden import load_config
    config = load_config(quiet=True)
    if config['MAIN'].getboolean('hide_private_info') is True:
        return '[Hidden]'
    else:
        return txt


@jinja2.contextfilter
@warden.app_template_filter()
def jformat(context, n, places, divisor=1):
    if n is None:
        return "-"
    else:
        try:
            n = float(n)
            n = n / divisor
            if n == 0:
                return "-"
        except ValueError:
            return "-"
        except TypeError:
            return (n)
        try:
            form_string = "{0:,.{prec}f}".format(n, prec=places)
            return form_string
        except (ValueError, KeyError):
            return "-"


@jinja2.contextfilter
@warden.app_template_filter()
def shorten(context, s, num=200, placeholder='[...]', html_over=True):
    if s is None:
        return "-"
    s = str(s)
    num = int(num)
    if num <= 0:
        return '-'
    size = len(s)
    if size < num:
        return s

    num = num - len(placeholder)

    left = int(num / 2)
    right = num - left
    out = s[0:left] + placeholder + s[size - right:]
    if html_over is True:
        out = "<span data-toggle='tooltip' title='" + s + "'>" + out + "</span>"
    return out


# Jinja filter - time to time_ago
@jinja2.contextfilter
@warden.app_template_filter()
def time_ago(context, time=False):
    if type(time) is str:
        try:
            time = int(time)
        except TypeError:
            return ""
        except ValueError:
            # Try different parser
            time = datetime.strptime(time, '%m-%d-%Y (%H:%M)')
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    else:
        return ("")
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ""

    if day_diff == 0:
        if second_diff < 10:
            return "Just Now"
        if second_diff < 60:
            return str(int(second_diff)) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(int(day_diff)) + " days ago"
    if day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"


@jinja2.contextfilter
@warden.app_template_filter()
def running_status(context, value=None):
    if value is None:
        return ""
    if value is True:
        return "<span class='text-success'><i class='far fa-check-circle'></i></span>"
    if value is False:
        return "<span class='text-danger'><i class='fas fa-exclamation-triangle'></i></span>"
