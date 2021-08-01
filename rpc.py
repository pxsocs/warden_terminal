from dashboard import load_config
import os
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException


def rpc_connect():
    from node_warden import load_config
    config = load_config(True)
    # Check if running inside umbrel OS and if environmental variables
    # are available
    from node_warden import pickle_it
    inside_umbrel = pickle_it('load', 'inside_umbrel.pkl')
    raspiblitz = pickle_it('load', 'raspiblitz_detected.pkl')
    mynode = pickle_it('load', 'mynode_detected.pkl')

    if raspiblitz is True:
        raspi_dict = pickle_it('load', 'raspi_bitcoin.pkl')
        if raspi_dict != 'file not found':
            try:
                rpc_user = raspi_dict['rpcuser']
                rpc_password = raspi_dict['rpcpassword']
                rpc_bind = raspi_dict['main.rpcbind']
                rpc_ip, rpc_port = rpc_bind.split(":")
            except Exception:
                raspiblitz = False

    elif mynode is True:
        mynode_dict = pickle_it('load', 'mynode_bitcoin.pkl')
        rpc_user = mynode_dict['rpc_user']
        rpc_password = mynode_dict['rpc_password']
        url = mynode_dict['rpc_ip']
        # End URL in / if not there
        if url[-1] != '/':
            url += '/'
            if 'http' not in url:
                url = 'http://' + url
        rpc_ip = url
        rpc_port = mynode_dict['rpc_port']

    elif inside_umbrel is True:
        umbrel_dict = pickle_it('load', 'umbrel_dict.pkl')
        if umbrel_dict != 'file not found':
            try:
                rpc_user = umbrel_dict['RPC_USER']
                rpc_password = umbrel_dict['RPC_PASSWORD']
                url = umbrel_dict['BITCOIN_HOST']
                # End URL in / if not there
                if url[-1] != '/':
                    url += '/'
                    if 'http' not in url:
                        url = 'http://' + url
                rpc_ip = url
                rpc_port = umbrel_dict['RPC_PORT']
            except Exception:
                inside_umbrel = False

    else:
        # Get the config info as default
        if config['BITCOIN_RPC'].get('ip_address') != 'None':
            rpc_user = config['BITCOIN_RPC'].get('BTCEXP_BITCOIND_USER')
            rpc_password = config['BITCOIN_RPC'].get('BTCEXP_BITCOIND_PASS')
            rpc_ip = config['BITCOIN_RPC'].get('BTCEXP_BITCOIND_HOST')
            rpc_port = config['BITCOIN_RPC'].get('BTCEXP_BITCOIND_PORT')
        else:
            # If not, let's try to get the environment variables
            # These are standard for Umbrel for example
            rpc_user = os.environ.get('BTCEXP_BITCOIND_USER')
            rpc_password = os.environ.get('BTCEXP_BITCOIND_PASS')
            rpc_ip = os.environ.get('BTCEXP_BITCOIND_HOST')
            rpc_port = os.environ.get('BTCEXP_BITCOIND_PORT')

    try:
        rpc_ip = rpc_ip.replace('http:', '')
        rpc_ip = rpc_ip.replace('/', '')
        rpc_connection = AuthServiceProxy(
            f"http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}",
            timeout=60)
    except Exception:
        rpc_connection = None

    return (rpc_connection)


def btc_network():
    return (os.environ.get('BTCEXP_BITCOIND_NETWORK'))


# Result from getblockchaininfo():
# {
#    "chain":"regtest",
#    "blocks":0,
#    "headers":0,
#    "bestblockhash":"0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206",
#    "difficulty":"Decimal(""4.656542373906925E-10"")",
#    "mediantime":1296688602,
#    "verificationprogress":1,
#    "initialblockdownload":true,
#    "chainwork":"0000000000000000000000000000000000000000000000000000000000000002",
#    "size_on_disk":293,
#    "pruned":false,
#    "softforks":{
#       "bip34":{
#          "type":"buried",
#          "active":false,
#          "height":500
#       },
#       "bip66":{
#          "type":"buried",
#          "active":false,
#          "height":1251
#       },
#       "bip65":{
#          "type":"buried",
#          "active":false,
#          "height":1351
#       },
#       "csv":{
#          "type":"buried",
#          "active":false,
#          "height":432
#       },
#       "segwit":{
#          "type":"buried",
#          "active":true,
#          "height":0
#       },
#       "testdummy":{
#          "type":"bip9",
#          "bip9":{
#             "status":"defined",
#             "start_time":0,
#             "timeout":9223372036854775807,
#             "since":0,
#             "min_activation_height":0
#          },
#          "active":false
#       },
#       "taproot":{
#          "type":"bip9",
#          "bip9":{
#             "status":"active",
#             "start_time":-1,
#             "timeout":9223372036854775807,
#             "since":0,
#             "min_activation_height":0
#          },
#          "height":0,
#          "active":true
#       }
#    },
#    "warnings":""
# }

# getbalances()
# {
#    "mine":{
#       "trusted":"Decimal(""5450.00000000"")",
#       "untrusted_pending":"Decimal(""0E-8"")",
#       "immature":"Decimal(""781.25000000"")"
#    }
# }

# # getnetworkinfo
#  {
#    "version":210100,
#    "subversion":"/Satoshi:0.21.1/",
#    "protocolversion":70016,
#    "localservices":"000000000000044d",
#    "localservicesnames":[
#       "NETWORK",
#       "BLOOM",
#       "WITNESS",
#       "COMPACT_FILTERS",
#       "NETWORK_LIMITED"
#    ],
#    "localrelay":true,
#    "timeoffset":0,
#    "networkactive":true,
#    "connections":0,
#    "connections_in":0,
#    "connections_out":0,
#    "networks":[
#       {
#          "name":"ipv4",
#          "limited":false,
#          "reachable":true,
#          "proxy":"10.21.21.11:9050",
#          "proxy_randomize_credentials":true
#       },
#       {
#          "name":"ipv6",
#          "limited":false,
#          "reachable":true,
#          "proxy":"10.21.21.11:9050",
#          "proxy_randomize_credentials":true
#       },
#       {
#          "name":"onion",
#          "limited":false,
#          "reachable":true,
#          "proxy":"10.21.21.11:9050",
#          "proxy_randomize_credentials":true
#       }
#    ],
#    "relayfee":"Decimal(""0.00001000"")",
#    "incrementalfee":"Decimal(""0.00001000"")",
#    "localaddresses":[

#    ],
#    "warnings":""
# }

# listtransactions()
# [
#    {
#       "address":"bcrt1q35t52c8jyze9036g8vjz5dey9wsrt056afp96d",
#       "category":"immature",
#       "amount":"Decimal(""6.25000000"")",
#       "label":"",
#       "vout":0,
#       "confirmations":10,
#       "generated":true,
#       "blockhash":"491ba5f9db237d48605a75d059eb8b10b675b007e99c0e921369cd4c5d5daa17",
#       "blockheight":515,
#       "blockindex":0,
#       "blocktime":1625941547,
#       "txid":"9b82f4c10d72ae4ce771d2270e80d855193fdbc59eb662c80b9eb65ef39e0ab5",
#       "walletconflicts":[

#       ],
#       "time":1625941547,
#       "timereceived":1625941547,
#       "bip125-replaceable":"no"
#    },
#    {
#       "address":"bcrt1q35t52c8jyze9036g8vjz5dey9wsrt056afp96d",
#       "category":"immature",
#       "amount":"Decimal(""6.25000000"")",
#       "label":"",
#       "vout":0,
#       "confirmations":9,
#       "generated":true,
#       "blockhash":"4306f4215c428c40936294c292e319d10d274dbfb232dbb4b41cbd41ec81f8dd",
#       "blockheight":516,
#       "blockindex":0,
#       "blocktime":1625941547,
#       "txid":"631f313b0d5def5ce198276b8570e6ae3946fe658471406d8f4d3310516e2069",
#       "walletconflicts":[

#       ],
#       "time":1625941547,
#       "timereceived":1625941547,
#       "bip125-replaceable":"no"
#    },
#    {
#       "address":"bcrt1q35t52c8jyze9036g8vjz5dey9wsrt056afp96d",
#       "category":"immature",
#       "amount":"Decimal(""6.25000000"")",
#       "label":"",
#       "vout":0,
#       "confirmations":8,
#       "generated":true,
#       "blockhash":"76012cbbd0a4847afc01d972e5f22cb2455293e6abed0a6bfd1e597c2010d9cc",
#       "blockheight":517,
#       "blockindex":0,
#       "blocktime":1625941547,
#       "txid":"8815aaf0cf10deb3441330ac9d1b3d615016b64a84fc13ef2f0084054cbc59f4",
#       "walletconflicts":[

#       ],
#       "time":1625941547,
#       "timereceived":1625941547,
#       "bip125-replaceable":"no"
#    },
#    {
#       "address":"bcrt1q35t52c8jyze9036g8vjz5dey9wsrt056afp96d",
#       "category":"immature",
#       "amount":"Decimal(""6.25000000"")",
#       "label":"",
#       "vout":0,
#       "confirmations":7,
#       "generated":true,
#       "blockhash":"3c89cd2969902be8e0755db7ee98542eab299495515103704c81711c464a0fb8",
#       "blockheight":518,
#       "blockindex":0,
#       "blocktime":1625941547,
#       "txid":"2b1a0b8370155b6b0adc89e19306d2a9372422a059a5f1a75dd454bc00b05be0",
#       "walletconflicts":[

#       ],
#       "time":1625941547,
#       "timereceived":1625941547,
#       "bip125-replaceable":"no"
#    },
#    {
#       "address":"bcrt1q35t52c8jyze9036g8vjz5dey9wsrt056afp96d",
#       "category":"immature",
#       "amount":"Decimal(""6.25000000"")",
#       "label":"",
#       "vout":0,
#       "confirmations":6,
#       "generated":true,
#       "blockhash":"249e29e86f08fa01499a18e79824999c9c5c932beeb82cfd27a2a1a1e429da02",
#       "blockheight":519,
#       "blockindex":0,
#       "blocktime":1625941547,
#       "txid":"b4e4c2128e511f845bee67e235f47a55d253aaeeed64e70eabcb591cb091ea50",
#       "walletconflicts":[

#       ],
#       "time":1625941547,
#       "timereceived":1625941547,
#       "bip125-replaceable":"no"
#    },
#    {
#       "address":"bcrt1q35t52c8jyze9036g8vjz5dey9wsrt056afp96d",
#       "category":"immature",
#       "amount":"Decimal(""6.25000000"")",
#       "label":"",
#       "vout":0,
#       "confirmations":5,
#       "generated":true,
#       "blockhash":"7a85f906b16996eaa8e48255f96640ec58b2006794dd27f15ae831d2867ccec3",
#       "blockheight":520,
#       "blockindex":0,
#       "blocktime":1625941547,
#       "txid":"b8ceebe352a9662c733a6a08775fdada2607253be665ac0b2b2d610edb6415e1",
#       "walletconflicts":[

#       ],
#       "time":1625941547,
#       "timereceived":1625941547,
#       "bip125-replaceable":"no"
#    },
#    {
#       "address":"bcrt1q35t52c8jyze9036g8vjz5dey9wsrt056afp96d",
#       "category":"immature",
#       "amount":"Decimal(""6.25000000"")",
#       "label":"",
#       "vout":0,
#       "confirmations":4,
#       "generated":true,
#       "blockhash":"2c5b71f199d32ba0871853be205a4d02e2c6a7a173f0ebbd2ed20d1576ca22d5",
#       "blockheight":521,
#       "blockindex":0,
#       "blocktime":1625941548,
#       "txid":"bc185cd682712f7af8039ea9a97e0e0371a64e7a8b291ff18e234fcd0e72bd2c",
#       "walletconflicts":[

#       ],
#       "time":1625941547,
#       "timereceived":1625941547,
#       "bip125-replaceable":"no"
#    },
#    {
#       "address":"bcrt1q35t52c8jyze9036g8vjz5dey9wsrt056afp96d",
#       "category":"immature",
#       "amount":"Decimal(""6.25000000"")",
#       "label":"",
#       "vout":0,
#       "confirmations":3,
#       "generated":true,
#       "blockhash":"7f80b25723d881b608cea864a154cb9afda63aa075da69b594a8a68e0c709ff0",
#       "blockheight":522,
#       "blockindex":0,
#       "blocktime":1625941548,
#       "txid":"9acf08d2ceacdb79813a80fc3497b5624195c70e376d74faa157a17d511b2e81",
#       "walletconflicts":[

#       ],
#       "time":1625941547,
#       "timereceived":1625941547,
#       "bip125-replaceable":"no"
#    },
#    {
#       "address":"bcrt1q35t52c8jyze9036g8vjz5dey9wsrt056afp96d",
#       "category":"immature",
#       "amount":"Decimal(""6.25000000"")",
#       "label":"",
#       "vout":0,
#       "confirmations":2,
#       "generated":true,
#       "blockhash":"410c12f7b7b11eb5c83309fab42aec2d7d9c4345e1a01c800728b6ffd433414e",
#       "blockheight":523,
#       "blockindex":0,
#       "blocktime":1625941548,
#       "txid":"5933a7ebee2f336d2401c0ae33886d8c9f0b94489b4fadd7a9061e827d61a3fc",
#       "walletconflicts":[

#       ],
#       "time":1625941547,
#       "timereceived":1625941547,
#       "bip125-replaceable":"no"
#    },
#    {
#       "address":"bcrt1q35t52c8jyze9036g8vjz5dey9wsrt056afp96d",
#       "category":"immature",
#       "amount":"Decimal(""6.25000000"")",
#       "label":"",
#       "vout":0,
#       "confirmations":1,
#       "generated":true,
#       "blockhash":"3d30adde7463ffd34f01c5add923221bcec584d0892f8c8d64ae69ef2547a14d",
#       "blockheight":524,
#       "blockindex":0,
#       "blocktime":1625941548,
#       "txid":"6368f00d73eb2331185b78ea61c11a8897f96744cfa07486a871d2d52cd1af64",
#       "walletconflicts":[

#       ],
#       "time":1625941547,
#       "timereceived":1625941547,
#       "bip125-replaceable":"no"
#    }
# ]


def get_whitepaper():
    rpc_connection = rpc_connect()
    hash = "54e48e5f5c656b26c3bca14a8c95aa583d07ebe84dde3b7dd4a78f4e4186e713"
    outputs_prun = []
    for i in range(0, 946):
        outputs_prun.append(rpc_connection.gettxout(hash, i))

    pdf = ""
    for output in outputs_prun[:-1]:
        cur = 4
        pdf += output["result"]["scriptPubKey"]["hex"][cur:cur + 130]
        cur += 132
        pdf += output["result"]["scriptPubKey"]["hex"][cur:cur + 130]
        cur += 132
        pdf += output["result"]["scriptPubKey"]["hex"][cur:cur + 130]
    pdf += outputs_prun[-1]["result"]["scriptPubKey"]["hex"][4:-4]

    from pathlib import Path
    filename = Path('bitcoin_whitepaper_from_node.pdf')

    with open(filename, "w") as text_file:
        text_file.write(pdf)

    return (f"Success. File {str(filename)} saved.")
