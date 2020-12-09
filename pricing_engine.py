# Class to include several price providers that work together to update a
# list of pricing databases
# The databases are saved in the pickle format as pandas df for later use
# The field dictionary is a list of column names for the provider to
# associate with the standardized field names for the dataframe
# Standardized field names:
# open, high, low, close, volume
import json
import os
import urllib
import csv
from datetime import datetime

import pandas as pd
import requests

from connections import tor_request
from decorators import timing


# Returns the current application path
def current_path():
    application_path = os.path.dirname(os.path.abspath(__file__))
    return (application_path)


# Returns the home path
def home_path():
    from pathlib import Path
    home = str(Path.home())
    return (home)


# Generic Requests will try each of these before failing
REALTIME_PROVIDER_PRIORITY = [
    'cc_realtime', 'aa_realtime_digital', 'aa_realtime_stock',
    'fp_realtime_stock'
]
FX_RT_PROVIDER_PRIORITY = ['aa_realtime_digital', 'cc_realtime']
HISTORICAL_PROVIDER_PRIORITY = [
    'cc_digital', 'aa_digital', 'aa_stock', 'cc_fx', 'aa_fx', 'fmp_stock',
    'bitmex'
]
FX_PROVIDER_PRIORITY = ['aa_fx', 'cc_fx']

# How to include new API providers (historical prices):
# Step 1:
#     Edit the PROVIDER_LIST dictionary at the end of the file.
#     See examples there and follow a similar pattern.
#     There are 2 types of providers in that list
#     a. Providers using an html request (like aa_digital)
#     b. Providers using an internal library (like bitmex)
# Step 2:
#     Edit the price parser function to include a new if statement
#     for the new provider. Follow the examples to return a pandas
#     dataframe.
#     Errors can be returned to the self.errors variable
#     on error, return df as None (this will signal an error)
# Notes:
#     Data is saved locally to a pickle file to be used during
#     the same day. File format is <TICKER>_<PROVIDER.NAME>.price
#     see ./pricing_data folder for samples
# Including realtime providers:
# Step 1:
#     follow step 1 above.
# Step 2:
#     edit the realtime function to parse the date correctly and
#     return a price float

# _____________________________________________
# Classes go here
# _____________________________________________


class PriceProvider:
    # This class manages a list of all pricing providers
    def __init__(self,
                 name,
                 base_url,
                 ticker_field,
                 field_dict=None,
                 doc_link=None,
                 replace_ticker=None):
        # field dict includes all fields to be passed to the URL
        # for example, for Alphavantage
        # name = 'Alphavantage_digital'
        # base-url = 'https://www.alphavantage.co/query'
        # ticker_field = 'symbol'
        # field_dict = {'function': 'DIGITAL_CURRENCY_DAILY',
        #               'market': 'CNY',
        #               'apikey': 'demo')
        # doc_link = 'https://www.alphavantage.co/documentation/'
        # parse_dict = {'open' : '1a. open (USD)', ...}
        self.name = name.lower()
        self.base_url = base_url
        self.ticker_field = ticker_field
        self.field_dict = field_dict
        self.doc_link = doc_link
        if self.field_dict is not None:
            try:
                self.url_args = "&" + urllib.parse.urlencode(field_dict)
            except AttributeError:
                self.url_args = "&" + urllib.urlencode(field_dict)
        self.errors = []
        self.replace_ticker = replace_ticker

    def request_data(self, ticker):
        data = None
        if self.base_url is not None:
            ticker = ticker.upper()
            globalURL = (self.base_url + "?" + self.ticker_field + "=" +
                         ticker + self.url_args)
            # Some APIs use the ticker without a ticker field i.e. xx.xx./AAPL&...
            # in these cases, we pass the ticker field as empty
            if self.ticker_field == '':
                if self.url_args[0] == '&':
                    self.url_args = self.url_args.replace('&', '?', 1)
                globalURL = (self.base_url + "/" + ticker + self.url_args)
            # Some URLs are in the form http://www.www.www/ticker_field/extra_fields?
            if self.replace_ticker is not None:
                globalURL = self.base_url.replace('ticker_field', ticker)
            request = tor_request(globalURL)
            try:
                data = request.json()
            except Exception:
                try:  # Try again - some APIs return a json already
                    data = json.loads(request)
                except Exception as e:
                    self.errors.append(e)
        return (data)


# PriceData Class Information
# Example on how to create a ticker class (PriceData)
# provider = PROVIDER_LIST['cc_digital']
# btc = PriceData("BTC", provider)
# btc.errors:       Any error messages
# btc.provider:     Provider being used for requests
# btc.filename:     Local filename where historical prices are saved
# Other info:
# btc.ticker, btc.last_update, btc.first_update, btc.last_close
# btc.update_history(force=False)
# btc.df_fx(currency, fx_provider): returns a df with
#                                   prices and fx conversions
# btc.price_ondate(date)
# btc.price_parser(): do not use directly. This is used to parse
#                     the requested data from the API provider
# btc.realtime(provider): returns realtime price (float)
class PriceData():
    # All methods related to a ticker
    def __init__(self, ticker, provider):
        # providers is a list of pricing providers
        # ex: ['alphavantage', 'Yahoo']
        self.ticker = ticker.upper()
        self.provider = provider
        self.errors = []
        # makesure file path exists

    def realtime(self, rt_provider):
        # This is the parser for realtime prices.
        # Data should be parsed so only the price is returned
        price_request = rt_provider.request_data(self.ticker)
        price = None
        if rt_provider.name == 'ccrealtime':
            try:
                price = (price_request['USD'])
            except Exception as e:
                self.errors.append(e)

        if rt_provider.name == 'aarealtime':
            try:
                price = (price_request['Realtime Currency Exchange Rate']
                         ['5. Exchange Rate'])
            except Exception:
                try:
                    price = (price_request['price_data']['last_close'])
                except Exception as e:
                    self.errors.append(e)

        if rt_provider.name == 'aarealtimestock':
            try:
                price = (price_request['Global Quote']['05. price'])
            except Exception:
                try:
                    price = (price_request['price_data']['last_close'])
                except Exception as e:
                    self.errors.append(e)

        if rt_provider.name == 'ccrealtimefull':
            try:
                price = (price_request['RAW'][self.ticker]['USD'])
            except Exception as e:
                self.errors.append(e)

        if rt_provider.name == 'fprealtimestock':
            try:
                price = (price_request['price'])
            except Exception as e:
                self.errors.append(e)

        return price


class ApiKeys():
    # returns current stored keys in the api_keys.conf file
    # makesure file path exists
    def __init__(self):
        self.filename = 'warden/api_keys.conf'
        self.filename = os.path.join(home_path(), self.filename)
        try:
            os.makedirs(os.path.dirname(self.filename))
        except OSError as e:
            if e.errno != 17:
                raise

    def loader(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as fp:
                    data = json.load(fp)
                    return (data)
            except Exception as e:
                pass
        else:
            # File not found, let's construct a new one
            empty_api = {
                "alphavantage": {
                    "api_key": "AA_TEMP_APIKEY"
                },
                "bitmex": {
                    "api_key": None,
                    "api_secret": None
                },
                "dojo": {
                    "onion": None,
                    "api_key": None,
                    "token": "error"
                }
            }
            return (empty_api)

    def saver(self, api_dict):
        try:
            with open(self.filename, 'w') as fp:
                json.dump(api_dict, fp)
        except Exception:
            pass


# Class instance with api keys loader and saver
api_keys_class = ApiKeys()
api_keys = api_keys_class.loader()


# Loop through all providers to get the first non-empty df
def price_data(ticker):
    GBTC_PROVIDER_PRIORITY = [
        'aa_stock', 'cc_fx', 'aa_fx', 'fmp_stock', 'bitmex'
    ]
    if ticker == 'GBTC':
        provider_list = GBTC_PROVIDER_PRIORITY
    else:
        provider_list = HISTORICAL_PROVIDER_PRIORITY

    for provider in provider_list:
        price_data = PriceData(ticker, PROVIDER_LIST[provider])
        if price_data.df is not None:
            break
    return (price_data)


# Returns price data in current user's currency
def price_data_fx(ticker):  # BTC
    FX = fx_rate()['base']
    GBTC_PROVIDER_PRIORITY = [
        'aa_stock', 'cc_fx', 'aa_fx', 'fmp_stock', 'bitmex'
    ]
    if ticker == 'GBTC':
        provider_list = GBTC_PROVIDER_PRIORITY
    else:
        provider_list = HISTORICAL_PROVIDER_PRIORITY

    for provider in provider_list:
        price_data = PriceData(ticker, PROVIDER_LIST[provider])
        if price_data.df is not None:
            break
    # Loop through FX providers until a df is filled
    for provider in FX_PROVIDER_PRIORITY:
        prices = price_data.df_fx(FX, PROVIDER_LIST[provider])
        if prices is not None:
            break
    return (prices)


# Returns realtime price for a ticker using the provider list
# Price is returned in USD
def price_data_rt(ticker, priority_list=REALTIME_PROVIDER_PRIORITY):
    if ticker == 'USD':
        return None
    for provider in priority_list:
        price_data = PriceData(ticker, PROVIDER_LIST[provider])
        if price_data.realtime(PROVIDER_LIST[provider]) is not None:
            break
    return (price_data.realtime(PROVIDER_LIST[provider]))


def GBTC_premium(price):
    # Calculates the current GBTC premium in percentage points
    # to BTC (see https://grayscale.co/bitcoin-trust/)
    SHARES = 0.00095812  # as of 8/1/2020
    fairvalue = price_data_rt("BTC") * SHARES
    premium = (price / fairvalue) - 1
    return fairvalue, premium


# Returns full realtime price for a ticker using the provider list
# Price is returned in USD
def price_grabber_rt_full(ticker, priority_list=['cc', 'aa', 'fp']):
    for provider in priority_list:
        price_data = price_data_rt_full(ticker, provider)
        if price_data is not None:
            return {'provider': provider, 'data': price_data}
    return None


def price_data_rt_full(ticker, provider):
    # Function to get a complete data set for realtime prices
    # Loop through the providers to get the following info:
    # price, chg, high, low, volume, mkt cap, last_update, source
    # For some specific assets, a field 'note' can be passed and
    # will replace volume and market cap at the main page
    # ex: GBTC premium can be calculated here
    # returns a list with the format:
    # price, last_update, high, low, chg, mktcap,
    # last_up_source, volume, source, notes
    # All data returned in USD
    # -----------------------------------------------------------
    # This function is used to grab a single price that was missing from
    # the multiprice request. Since this is a bit more time intensive, it's
    # separated so it can be memoized for a period of time (this price will
    # not refresh as frequently)
    # default: timeout=30
    from warden_modules import (FX, FX_RATE)
    if provider == 'cc':
        multi_price = multiple_price_grab(ticker, 'USD,' + FX)
        try:
            # Parse the cryptocompare data
            price = multi_price["RAW"][ticker][FX]["PRICE"]
            price = float(price * FX_RATE)
            high = float(multi_price["RAW"][ticker][FX]["HIGHDAY"] * FX_RATE)
            low = float(multi_price["RAW"][ticker][FX]["LOWDAY"] * FX_RATE)
            chg = multi_price["RAW"][ticker][FX]["CHANGEPCT24HOUR"]
            mktcap = multi_price["DISPLAY"][ticker][FX]["MKTCAP"]
            volume = multi_price["DISPLAY"][ticker][FX]["VOLUME24HOURTO"]
            last_up_source = multi_price["RAW"][ticker][FX]["LASTUPDATE"]
            source = multi_price["DISPLAY"][ticker][FX]["LASTMARKET"]
            last_update = datetime.now()
            notes = None
            return (price, last_update, high, low, chg, mktcap, last_up_source,
                    volume, source, notes)
        except Exception:
            return (None)
    if provider == 'aa':
        try:
            globalURL = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&apikey='
            globalURL += api_keys['alphavantage'][
                'api_key'] + '&symbol=' + ticker
            data = tor_request(globalURL).json()
            price = float(data['Global Quote']['05. price']) * FX_RATE
            high = float(data['Global Quote']['03. high']) * FX_RATE
            low = float(data['Global Quote']['04. low']) * FX_RATE
            chg = data['Global Quote']['10. change percent'].replace('%', '')
            try:
                chg = float(chg)
            except Exception:
                chg = chg
            mktcap = '-'
            volume = '-'
            last_up_source = '-'
            last_update = '-'
            source = 'Alphavantage'
            notes = None

            # Start Notes methods for specific assets. For example, for
            # GBTC we report the premium to BTC
            if ticker == 'GBTC':
                fairvalue, premium = GBTC_premium(
                    float(data['Global Quote']['05. price']))
                fairvalue = "{0:,.2f}".format(fairvalue)
                premium = "{0:,.2f}".format(premium * 100)
                notes = "Fair Value: " + fairvalue + "<br>Premium: " + premium + "%"
            return (price, last_update, high, low, chg, mktcap, last_up_source,
                    volume, source, notes)
        except Exception:
            return None

    if provider == 'fp':
        try:
            globalURL = 'https://financialmodelingprep.com/api/v3/stock/real-time-price/'
            globalURL += ticker
            data = tor_request(globalURL).json()
            price = float(data['price']) * FX_RATE
            high = '-'
            low = '-'
            chg = 0
            mktcap = '-'
            volume = '-'
            last_up_source = '-'
            last_update = '-'
            source = 'FP Modeling API'
            notes = None
            return (price, last_update, high, low, chg, mktcap, last_up_source,
                    volume, source, notes)
        except Exception:
            return None


def fxsymbol(fx, output='symbol'):
    # Gets an FX 3 letter symbol and returns the HTML symbol
    # Sample outputs are:
    # "EUR": {
    # "symbol": "",
    # "name": "Euro",
    # "symbol_native": "",
    # "decimal_digits": 2,
    # "rounding": 0,
    # "code": "EUR",
    # "name_plural": "euros"
    filename = os.path.join(current_path(), 'static/json_files/currency.json')
    with open(filename) as fx_json:
        fx_list = json.load(fx_json)
    try:
        out = fx_list[fx][output]
    except Exception:
        if output == 'all':
            return (fx_list[fx])
        out = fx
    return (out)


# Gets Currency data for current user
# Setting a timeout to 10 as fx rates don't change so often
def fx_rate(FX='USD'):
    # This grabs the realtime current currency conversion against USD
    try:
        # get fx rate
        rate = {}
        rate['base'] = FX
        rate['symbol'] = fxsymbol(FX)
        rate['name'] = fxsymbol(FX, 'name')
        rate['name_plural'] = fxsymbol(FX, 'name_plural')
        rate['cross'] = "USD" + " / " + FX
        try:
            rate['fx_rate'] = 1 / (float(
                price_data_rt(FX, FX_RT_PROVIDER_PRIORITY)))
        except Exception:
            rate['fx_rate'] = 1
    except Exception as e:
        rate = {}
        rate['error'] = ("Error: " + str(e))
        rate['fx_rate'] = 1
    return (rate)


# For Tables that need multiple prices at the same time, it's quicker to get
# a single price request
# This will attempt to get all prices from cryptocompare api and return a single df
# If a price for a security is not found, other rt providers will be used.
def multiple_price_grab(tickers, fx):
    # tickers should be in comma sep string format like "BTC,ETH,LTC"
    baseURL = \
        "https://min-api.cryptocompare.com/data/pricemultifull?fsyms="\
        + tickers + "&tsyms=" + fx + "&&api_key=9863dbe4217d98738f4ab58137007d24d70da92031584ba31de78137e0576225"
    try:
        request = tor_request(baseURL)
    except requests.exceptions.ConnectionError:
        return ("ConnectionError")
    try:
        data = request.json()
    except AttributeError:
        data = "ConnectionError"
    return (data)


def get_price_ondate(ticker, date):
    try:
        price_class = price_data(ticker)
        price_ondate = price_class.price_ondate(date)
        return (price_ondate)
    except Exception:
        return (0)


def fx_price_ondate(base, cross, date):
    # Gets price conversion on date between 2 currencies
    # on a specific date
    try:
        provider = PROVIDER_LIST['cc_fx']
        if base == 'USD':
            price_base = 1
        else:
            base_class = PriceData(base, provider)
            price_base = base_class.price_ondate(date).close
        if cross == 'USD':
            price_cross = 1
        else:
            cross_class = PriceData(cross, provider)
            price_cross = cross_class.price_ondate(date).close
        conversion = float(price_cross) / float(price_base)
        return (conversion)
    except Exception:
        return (1)


# _____________________________________________
# Variables go here
# _____________________________________________
# List of API providers
# name: should be unique and contain only lowecase letters
PROVIDER_LIST = {
    'aa_digital':
    PriceProvider(name='alphavantagedigital',
                  base_url='https://www.alphavantage.co/query',
                  ticker_field='symbol',
                  field_dict={
                      'function': 'DIGITAL_CURRENCY_DAILY',
                      'market': 'USD',
                      'apikey': api_keys['alphavantage']['api_key']
                  },
                  doc_link='https://www.alphavantage.co/documentation/'),
    'aa_stock':
    PriceProvider(name='alphavantagestock',
                  base_url='https://www.alphavantage.co/query',
                  ticker_field='symbol',
                  field_dict={
                      'function': 'TIME_SERIES_DAILY',
                      'outputsize': 'full',
                      'apikey': api_keys['alphavantage']['api_key']
                  },
                  doc_link='https://www.alphavantage.co/documentation/'),
    'fmp_stock':
    PriceProvider(
        name='financialmodelingprep',
        base_url=
        'https://financialmodelingprep.com/api/v3/historical-price-full',
        ticker_field='',
        field_dict={
            'from': '2001-01-01',
            'to:': '2099-12-31'
        },
        doc_link='https://financialmodelingprep.com/developer/docs/#Stock-Price'
    ),
    'aa_fx':
    PriceProvider(name='alphavantagefx',
                  base_url='https://www.alphavantage.co/query',
                  ticker_field='to_symbol',
                  field_dict={
                      'function': 'FX_DAILY',
                      'outputsize': 'full',
                      'from_symbol': 'USD',
                      'apikey': api_keys['alphavantage']['api_key']
                  },
                  doc_link='https://www.alphavantage.co/documentation/'),
    'cc_digital':
    PriceProvider(
        name='ccdigital',
        base_url='https://min-api.cryptocompare.com/data/histoday',
        ticker_field='fsym',
        field_dict={
            'tsym':
            'USD',
            'allData':
            'true',
            'api_key':
            '9863dbe4217d98738f4ab58137007d24d70da92031584ba31de78137e0576225'
        },
        doc_link=
        'https://min-api.cryptocompare.com/documentation?key=Historical&cat=dataHistoday'
    ),
    'cc_fx':
    PriceProvider(
        name='ccfx',
        base_url='https://min-api.cryptocompare.com/data/histoday',
        ticker_field='tsym',
        field_dict={
            'fsym':
            'USD',
            'allData':
            'true',
            'api_key':
            '9863dbe4217d98738f4ab58137007d24d70da92031584ba31de78137e0576225'
        },
        doc_link=
        'https://min-api.cryptocompare.com/documentation?key=Historical&cat=dataHistoday'
    ),
    'bitmex':
    PriceProvider(name='bitmex',
                  base_url=None,
                  ticker_field=None,
                  field_dict={
                      'api_key': api_keys['bitmex']['api_key'],
                      'api_secret': api_keys['bitmex']['api_secret'],
                      'testnet': False
                  },
                  doc_link='https://www.bitmex.com/api/explorer/'),
    'cc_realtime':
    PriceProvider(
        name='ccrealtime',
        base_url='https://min-api.cryptocompare.com/data/price',
        ticker_field='fsym',
        field_dict={
            'tsyms':
            'USD',
            'api_key':
            '9863dbe4217d98738f4ab58137007d24d70da92031584ba31de78137e0576225'
        },
        doc_link=None),
    'cc_realtime_full':
    PriceProvider(
        name='ccrealtimefull',
        base_url='https://min-api.cryptocompare.com/data/pricemultifull',
        ticker_field='fsyms',
        field_dict={
            'tsyms':
            'USD',
            'api_key':
            '9863dbe4217d98738f4ab58137007d24d70da92031584ba31de78137e0576225'
        },
        doc_link=
        'https://min-api.cryptocompare.com/documentation?key=Price&cat=multipleSymbolsFullPriceEndpoint'
    ),
    'aa_realtime_digital':
    PriceProvider(name='aarealtime',
                  base_url='https://www.alphavantage.co/query',
                  ticker_field='from_currency',
                  field_dict={
                      'function': 'CURRENCY_EXCHANGE_RATE',
                      'to_currency': 'USD',
                      'apikey': api_keys['alphavantage']['api_key']
                  },
                  doc_link='https://www.alphavantage.co/documentation/'),
    'aa_realtime_stock':
    PriceProvider(name='aarealtimestock',
                  base_url='https://www.alphavantage.co/query',
                  ticker_field='symbol',
                  field_dict={
                      'function': 'GLOBAL_QUOTE',
                      'apikey': api_keys['alphavantage']['api_key']
                  },
                  doc_link='https://www.alphavantage.co/documentation/'),
    'fp_realtime_stock':
    PriceProvider(
        name='fprealtimestock',
        base_url=
        'https://financialmodelingprep.com/api/v3/stock/real-time-price',
        ticker_field='',
        field_dict='',
        doc_link='https://financialmodelingprep.com/developer/docs/#Stock-Price'
    )
}


def fx_list():
    filename = os.path.join(current_path(),
                            'static/csv_files/physical_currency_list.csv')
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        fiat_dict = {rows[0]: (rows[1]) for rows in reader}
    # Convert dict to list
    fx_list = [(k, k + ' | ' + v) for k, v in fiat_dict.items()]
    fx_list.sort()
    return (fx_list)


def is_currency(id):
    # Return true if id is in list of currencies
    found = ([item for item in fx_list() if item[0] == id])
    if found != []:
        return True
    return False
