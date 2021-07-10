import os
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException


def rpc_connect():
    rpc_user = os.environ.get('BTCEXP_BITCOIND_USER')
    rpc_password = os.environ.get('BTCEXP_BITCOIND_PASS')
    rpc_ip = os.environ.get('BTCEXP_BITCOIND_HOST')
    rpc_port = os.environ.get('BTCEXP_BITCOIND_PORT')
    try:
        rpc_connection = AuthServiceProxy(
            f"http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}",
            timeout=60)
    except Exception:
        rpc_connection = None

    return (rpc_connection)


def btc_network():
    return (os.environ.get('BTCEXP_BITCOIND_NETWORK'))