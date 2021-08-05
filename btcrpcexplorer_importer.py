import requests
import json
from datetime import datetime

from bs4 import BeautifulSoup
from node_warden import pickle_it


# WebCrawler to get json info from BTC-RPC-EXPLORER web
def crawler(url=None, port=None):
    consolidated_dict = {}
    url = 'umbrel.local'
    port = 3002

    end_point_list = ['node-details', 'peers']

    for endpoint in end_point_list:

        tmp_dict = {}
        web_url = 'http://' + url + ':' + str(port) + '/' + endpoint
        metadata = {}
        metadata['url'] = web_url
        page = requests.get(web_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        data = soup.find_all("code", {"class": "json"})
        # clean data
        for element in data:
            try:
                element = element.text.strip("<code>").strip("</code>")
                tmp_dict.update(json.loads(element))
            except Exception:
                pass

        consolidated_dict[endpoint] = tmp_dict

    pickle_it('save', 'btcrpc_refresh.pkl', datetime.now())
    pickle_it('save', 'btcrpc_json.pkl', consolidated_dict)
    return (consolidated_dict)


# Sample return
# {
#     'node-details': {
#         'chain':
#         'main',
#         'blocks':
#         694344,
#         'headers':
#         694344,
#         'bestblockhash':
#         '0000000000000000000987616aad095254ca83a34abd34c483057417c03dff6f',
#         'difficulty':
#         '14496442856349.12',
#         'mediantime':
#         1628181923,
#         'verificationprogress':
#         '0.9999964778058246',
#         'initialblockdownload':
#         False,
#         'chainwork':
#         '000000000000000000000000000000000000000020265f2a2568c9c71fd5c452',
#         'size_on_disk':
#         406424801725,
#         'pruned':
#         False,
#         'softforks': {
#             'bip34': {
#                 'type': 'buried',
#                 'active': True,
#                 'height': 227931
#             },
#             'bip66': {
#                 'type': 'buried',
#                 'active': True,
#                 'height': 363725
#             },
#             'bip65': {
#                 'type': 'buried',
#                 'active': True,
#                 'height': 388381
#             },
#             'csv': {
#                 'type': 'buried',
#                 'active': True,
#                 'height': 419328
#             },
#             'segwit': {
#                 'type': 'buried',
#                 'active': True,
#                 'height': 481824
#             },
#             'taproot': {
#                 'type': 'bip9',
#                 'bip9': {
#                     'status': 'locked_in',
#                     'start_time': 1619222400,
#                     'timeout': 1628640000,
#                     'since': 687456,
#                     'min_activation_height': 709632
#                 },
#                 'active': False
#             }
#         },
#         'warnings':
#         '',
#         'totalbytesrecv':
#         4081409331,
#         'totalbytessent':
#         907841598,
#         'timemillis':
#         1628183280589,
#         'uploadtarget': {
#             'timeframe': 86400,
#             'target': 0,
#             'target_reached': False,
#             'serve_historical_blocks': True,
#             'bytes_left_in_cycle': 0,
#             'time_left_in_cycle': 0
#         },
#         'version':
#         210100,
#         'subversion':
#         '/Satoshi:0.21.1/',
#         'protocolversion':
#         70016,
#         'localservices':
#         '000000000000044d',
#         'localservicesnames':
#         ['NETWORK', 'BLOOM', 'WITNESS', 'COMPACT_FILTERS', 'NETWORK_LIMITED'],
#         'localrelay':
#         True,
#         'timeoffset':
#         -1,
#         'networkactive':
#         True,
#         'connections':
#         10,
#         'connections_in':
#         0,
#         'connections_out':
#         10,
#         'networks': [{
#             'name': 'ipv4',
#             'limited': False,
#             'reachable': True,
#             'proxy': '10.21.21.11:9050',
#             'proxy_randomize_credentials': True
#         }, {
#             'name': 'ipv6',
#             'limited': False,
#             'reachable': True,
#             'proxy': '10.21.21.11:9050',
#             'proxy_randomize_credentials': True
#         }, {
#             'name': 'onion',
#             'limited': False,
#             'reachable': True,
#             'proxy': '10.21.21.11:9050',
#             'proxy_randomize_credentials': True
#         }],
#         'relayfee':
#         1e-05,
#         'incrementalfee':
#         1e-05,
#         'localaddresses': [],
#         'txindex': {
#             'synced': True,
#             'best_block_height': 691745
#         },
#         'basic block filter index': {
#             'synced': True,
#             'best_block_height': 691745
#         }
#     },
#     'peers': {
#         'id': 1420,
#         'addr': '137.116.213.143:8333',
#         'addrbind': '10.21.21.8:54124',
#         'addrlocal': '185.100.87.242:46710',
#         'network': 'ipv4',
#         'services': '0000000000000409',
#         'servicesnames': ['NETWORK', 'WITNESS', 'NETWORK_LIMITED'],
#         'relaytxes': True,
#         'lastsend': 1628183279,
#         'lastrecv': 1628183278,
#         'last_transaction': 1628183278,
#         'last_block': 0,
#         'bytessent': 2921017,
#         'bytesrecv': 7846358,
#         'conntime': 1628156923,
#         'timeoffset': 0,
#         'pingtime': 0.761336,
#         'minping': 0.392516,
#         'version': 70016,
#         'subver': '/Satoshi:0.21.1/',
#         'inbound': False,
#         'startingheight': 694293,
#         'synced_headers': 694344,
#         'synced_blocks': 694344,
#         'inflight': [],
#         'permissions': [],
#         'minfeefilter': 1e-05,
#         'bytessent_per_msg': {
#             'addrv2': 58348,
#             'feefilter': 32,
#             'getaddr': 24,
#             'getdata': 412619,
#             'getheaders': 1053,
#             'headers': 212,
#             'inv': 2267162,
#             'ping': 7040,
#             'pong': 168704,
#             'sendaddrv2': 24,
#             'sendcmpct': 66,
#             'sendheaders': 24,
#             'tx': 5535,
#             'verack': 24,
#             'version': 126,
#             'wtxidrelay': 24
#         },
#         'bytesrecv_per_msg': {
#             'addrv2': 126650,
#             'cmpctblock': 47704,
#             'feefilter': 32,
#             'getdata': 743,
#             'getheaders': 1053,
#             'headers': 5512,
#             'inv': 1519795,
#             'ping': 168704,
#             'pong': 7040,
#             'sendaddrv2': 24,
#             'sendcmpct': 66,
#             'sendheaders': 24,
#             'tx': 5968837,
#             'verack': 24,
#             'version': 126,
#             'wtxidrelay': 24
#         },
#         'connection_type': 'outbound-full-relay'
#     }
# }
