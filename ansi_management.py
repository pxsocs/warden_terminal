from ansi.colour import fg, fx
from datetime import datetime


def success(s):
    return (fg.green(s))


def error(s):
    return (fg.red(s))


def blue(s):
    return (fg.blue(s))


def warning(s):
    return (fg.yellow(s))


def yellow(s):
    return (fg.yellow(s))


def info(s):
    return (fg.boldgreen(s))


def muted(s):
    return (fg.gray(s))


def bold(s):
    return (fx.bold(s))


def clear_screen():
    for n in range(0, 100):
        print("")


def jformat(n, places, divisor=1):
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


def time_ago(time=False):
    if type(time) is str:
        try:
            time = int(time)
        except Exception:
            return ""
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


def cleanfloat(text):  # Function to clean CSV fields - leave only digits and .
    if isinstance(text, float):
        return text
    if text is None:
        return (0)
    acceptable = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "-"]
    str = ""
    for char in text:
        if char in acceptable:
            str = str + char
    str = float(str)
    return (str)


def ansi_to_html(text):
    import re

    COLOR_DICT = {
        '0': [(255, 0, 0), (128, 0, 0)],
        '31': [(255, 0, 0), (128, 0, 0)],
        '32': [(0, 255, 0), (0, 128, 0)],
        '33': [(255, 255, 0), (128, 128, 0)],
        '34': [(0, 0, 255), (0, 0, 128)],
        '35': [(255, 0, 255), (128, 0, 128)],
        '36': [(0, 255, 255), (0, 128, 128)],
        '37': [(0, 255, 255), (0, 128, 128)]
    }

    COLOR_REGEX = re.compile(
        r'\[(?P<arg_1>\d+)(;(?P<arg_2>\d+)(;(?P<arg_3>\d+))?)?m')

    BOLD_TEMPLATE = '<span style="color: rgb{}; font-weight: bolder">'
    LIGHT_TEMPLATE = '<span style="color: rgb{}">'

    text = "<pre class='codetext'>" + text + '</pre>'
    text = text.replace('\n', '<br>')
    text = text.replace('[m', '</span>')

    def single_sub(match):
        argsdict = match.groupdict()
        if argsdict['arg_3'] is None:
            if argsdict['arg_2'] is None:
                color, bold = argsdict['arg_1'], 0
            else:
                color, bold = argsdict['arg_1'], int(argsdict['arg_2'])
        else:
            color, bold = argsdict['arg_2'], int(argsdict['arg_3'])

        if bold:
            try:
                return BOLD_TEMPLATE.format(COLOR_DICT[color][1])
            except KeyError:
                return BOLD_TEMPLATE.format(COLOR_DICT['0'][1])

        try:
            return LIGHT_TEMPLATE.format(COLOR_DICT[color][0])
        except KeyError:
            return LIGHT_TEMPLATE.format(COLOR_DICT['0'][0])

    return COLOR_REGEX.sub(single_sub, text)