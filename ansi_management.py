from dependencies.ansi.colour import fg, fx


def success(s):
    return (fg.green(s))


def error(s):
    return (fg.red(s))


def warning(s):
    return (fg.yellow(s))


def info(s):
    return (fg.white(s))


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
