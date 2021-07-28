# Welcome to WARden Terminal

[![Powered by NgU](https://img.shields.io/badge/Powered%20by-NGU%20Technology-orange.svg)](https://bitcoin.org)

A light weight text based Bitcoin Dashboard for Linux based systems.
Displaying:

- Bitcoin Price in several currencies (currency list can be edited at config.ini)
- GBTC price and premium info
- Mempool information (fees, blocks, txs)
- Users currently logged in
- Tor Status
- Satoshi Quote Randomizer
- System info (CPU temperature, storage, etc)
- Wallet info [**coming soon**]

## Screenshot

![ScreenShot](/static/images/screen_shot.jpeg "App Screen Shot")

## Installation

Clone the git repository into any directory:

```bash
git clone https://github.com/pxsocs/warden_terminal
```

Install Requirements:

```bash
cd warden_terminal
pip3 install -r requirements.txt
```

Run the app:

```bash
python3 node_warden.py
```

**Optional if your node has a monitor attached and you want to force display to that monitor.**

If you are running a RaspiBlitz, MyNode or Umbrel, and installing through SSH follow this steps.

Find out which is the primary display:

```bash
who -a
```

Should output something like:

```s
admin@raspberrypi:~/warden_terminal $ who -a

           system boot  1970-01-01 01:00
pi       + tty1         2021-07-27 22:19 00:21        1097
           run-level 3  2021-07-27 22:19
admin    + pts/0        2021-07-28 14:55   .          7503 (192.168.1.123)
```

Take note of the system boot output. In the case above `tty1`.

Then run the below, replacing `tty1` if needed:

```bash
sudo chmod 666 /dev/tty1
```

Edit the config.ini file and change the `tty = /dev/tty` line to `tty = /dev/tty1` in this case:

```bash
nano config.ini
```

Save and close the file and run the program:

```bash
python3 node_warden.py &
```

## Enjoyed the app?

Consider making a donation.

tipping.me (Lightning): https://tippin.me/@alphaazeta
onchain: bc1q4fmyksw40vktte9n6822e0aua04uhmlez34vw5gv72zlcmrkz46qlu7aem

## FAQ:

### Getting a message that Tor is not running

You need Tor Running for the app to work. Instructions [here](https://2019.www.torproject.org/docs/debian.html.en).

### How to customize settings?

The `config.ini` file can be edited with:

```bash
nano config.ini
```

### Including price of BTC in other dirty fiat terms

Edit the list below in config.ini to remove and/or include other currencies.
`fx_list = ['USD','EUR', 'GBP', 'CAD']`

### Changing the font for large price widget

You can change the large text font field `large_text_font = standard` used to display bitcoin's price.
A list of available fonts can be found [here](http://www.figlet.org/).

### Changing the Screen Size may help to display more data

When running on console (no GUI), decreasing the font size may lead to better viewing results. 6x12 runs really well on a 8 inch or bigger screen. Instructions [here](https://www.raspberrypi-spy.co.uk/2014/04/how-to-change-the-command-line-font-size/#:~:text=Using%20the%20up%2Fdown%20arrow%20keys%20select%20%E2%80%9C16%C3%9732,the%20size%20of%20the%20default.) for Debian.

Enjoy

**Please note that this is ALPHA software. There is no guarantee that the
information and analytics are correct. Also expect no customer support. Issues are encouraged to be raised through GitHub but they will be answered on a best efforts basis.**
