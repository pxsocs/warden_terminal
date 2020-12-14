# Welcome to WARden Terminal

[![Powered by NGU](https://img.shields.io/badge/Powered%20by-NGU%20Technology-orange.svg)](https://bitcoin.org)

> warden (wɔːʳdən )
> A warden is responsible for making sure that the laws or regulations are obeyed.

![ScreenShot](/static/images/screen_shot.jpeg "App Screen Shot")

## Installation

Clone the git repository into any directory:

```bash
git clone https://github.com/pxsocs/warden_terminal
```

Then run:

```bash
cd warden_terminal
pip3 install -r requirements.txt
python3 node_warden.py
```

You need Tor Running for the app to work. Instructions [here](https://2019.www.torproject.org/docs/debian.html.en).

The `config.ini` file can be edited with:

```bash
nano config.ini
```

There you can edit the currencies, audio and other settings.

### Screen Size

When running on console (no GUI), decreasing the font size may lead to better viewing results. 6x12 runs really well on a 8 inch or bigger screen. Instructions [here](https://www.raspberrypi-spy.co.uk/2014/04/how-to-change-the-command-line-font-size/#:~:text=Using%20the%20up%2Fdown%20arrow%20keys%20select%20%E2%80%9C16%C3%9732,the%20size%20of%20the%20default.) for Debian.

Enjoy

**Please note that this is ALPHA software. There is no guarantee that the
information and analytics are correct. Also expect no customer support. Issues are encouraged to be raised through GitHub but they will be answered on a best efforts basis.**
