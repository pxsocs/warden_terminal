from dependencies.ansi.colour import fg, fx


def success(s):
    return (fg.green(s))


def error(s):
    return (fg.orange(s))


def warning(s):
    return (fg.yellow(s))


def info(s):
    return (fg.white(s))


def bold(s):
    return (fx.bold(s))


def clear_screen():
    for n in range(0, 100):
        print("")
