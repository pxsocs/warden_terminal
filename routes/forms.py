import pyfiglet
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, SelectField


class Settings(FlaskForm):
    from node_warden import load_config
    config = load_config(quiet=True)
    refresh = IntegerField("Widget scroll interval (seconds)",
                           default=config['MAIN'].getint('refresh'))

    price_refresh = IntegerField(
        "Price refresh interval (seconds)",
        default=config['MAIN'].getint('price_refresh_interval'))

    asc_font = SelectField("Terminal ASCII Large Text Font",
                           default=config['MAIN'].get('large_text_font'),
                           choices=pyfiglet.FigletFont.getFonts())

    submit = SubmitField("Save Changes")
