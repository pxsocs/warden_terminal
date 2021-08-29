# Creates a series of standardized elements for dashboards
# These are usefull for javascript ajax calls where
# they come out already formatted


def progress_bar(text=None,
                 value=0,
                 max=100,
                 min=0,
                 animated=False,
                 striped=True,
                 style='bg-info'):
    try:
        txt = "<div class='progress'> <div class='progress-bar  "
        if striped is True:
            txt += 'progress-bar-striped '
        txt += style + "' role='progressbar' style='width: 100%'"
        txt += " aria-valuenow='" + str(value) + "' aria-valuemin='" + str(
            min) + "'"
        txt += " aria-valuemax='" + str(max) + "'>" + str(
            text) + "</div></div>"
    except Exception as e:
        txt = f"<div class='text-alert'>[i] Error on widget: {e}</div>"

    return (txt)


class dataElement():
    def __init__(self):
        self.name = None
        self.value = None
        self.html_render = progress_bar

    def html(self):
        return self.html_render(self.value)
