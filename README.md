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

Then run:

```bash
cd warden_terminal
pip3 install -r requirements.txt
python3 node_warden.py
```

## FAQ:

### Can I auto load warden on start up on PI?

Yes. follow the steps below:

1. Edit the file launcer.sh and make sure it is pointing to the correct directory where warden terminal is. You can check the folder path by typing `pwd` while inside the WARden folder.

Should return something like:

> /home/umbrel/warden_terminal

Take note of this folder then:

```bash
nano launcher.sh
```

And change the cd home/...... to your folder above. CTRL+X and Y to save and exit.

2. Change the file permission of `launcher.sh`

```bash
chmod 755 launcher.sh
```

3. Add it as a cron job

```bash
sudo crontab -e
```

If prompted to select an editor, choose `/bin/nano`.

Scroll to the end of the file - last line and include the following line. **Make sure to change the directory to the one you noted with `pwd` above**

```bash
@reboot sh /home/umbrel/<your folder>/warden_terminal/launcher.sh &
```

CTRL + X
Y to save

4. Reboot

```bash
sudo reboot
```

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
