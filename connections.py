import requests
import socket
from time import time
from datetime import datetime


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def test_tor():
    response = {}
    session = requests.session()
    try:
        time_before = time()  # Save Ping time to compare
        r = session.get("http://httpbin.org/ip")
        time_after = time()
        pre_proxy_ping = time_after - time_before
        pre_proxy = r.json()
    except Exception as e:
        pre_proxy = pre_proxy_ping = "Connection Error: " + str(e)

    PORTS = ['9050', '9150']

    # Activate TOR proxies
    for PORT in PORTS:
        session.proxies = {
            "http": "socks5h://localhost:" + PORT,
            "https": "socks5h://localhost:" + PORT,
        }
        try:
            failed = False
            time_before = time()  # Save Ping time to compare
            r = session.get("http://httpbin.org/ip")
            time_after = time()
            post_proxy_ping = time_after - time_before
            post_proxy_difference = post_proxy_ping / pre_proxy_ping
            post_proxy = r.json()

            if pre_proxy["origin"] != post_proxy["origin"]:
                response = {
                    "pre_proxy": pre_proxy,
                    "post_proxy": post_proxy,
                    "post_proxy_ping":
                    "{0:.2f} seconds".format(post_proxy_ping),
                    "pre_proxy_ping": "{0:.2f} seconds".format(pre_proxy_ping),
                    "difference": "{0:.2f}".format(post_proxy_difference),
                    "status": True,
                    "port": PORT
                }
                return response
        except Exception as e:
            failed = True
            post_proxy_ping = post_proxy = "Failed checking TOR status. Error: " + str(
                e)

        if not failed:
            break

    response = {
        "pre_proxy": pre_proxy,
        "post_proxy": post_proxy,
        "post_proxy_ping": post_proxy_ping,
        "pre_proxy_ping": pre_proxy_ping,
        "difference": "-",
        "status": False,
        "port": "failed"
    }
    return response


def tor_request(url, tor_only=False, method="get", headers=None):
    # Tor requests takes arguments:
    # url:       url to get or post
    # tor_only:  request will only be executed if tor is available
    # method:    'get or' 'post'
    # Store TOR Status here to avoid having to check on all http requests
    TOR = test_tor()
    if '.local' in url:
        try:
            if method == "get":
                request = requests.get(url, timeout=10)
            if method == "post":
                request = requests.post(url, timeout=10)
            return (request)

        except requests.exceptions.ConnectionError:
            return "ConnectionError"

    if TOR["status"] is True:
        try:
            # Activate TOR proxies
            session = requests.session()
            session.proxies = {
                "http": "socks5h://localhost:" + TOR['port'],
                "https": "socks5h://localhost:" + TOR['port'],
            }
            if method == "get":
                if headers:
                    request = session.get(url, timeout=15, headers=headers)
                else:
                    request = session.get(url, timeout=15)
            if method == "post":
                request = session.post(url, timeout=15)

        except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
        ):
            return "ConnectionError"
    else:
        if tor_only:
            return "Tor not available"
        try:
            if method == "get":
                request = requests.get(url, timeout=10)
            if method == "post":
                request = requests.post(url, timeout=10)

        except requests.exceptions.ConnectionError:
            return "ConnectionError"

    return request


# Check Local Network for nodes and services
def scan_network():
    from node_warden import pickle_it, load_config

    host_list = [
        'umbrel.local', 'mynode.local', 'raspberrypi.local', 'ronindojo.local',
        'raspberrypi-2.local'
    ]

    # Additional node names can be added on config.ini - append here
    config = load_config(quiet=True)
    try:
        config_node = config['MAIN'].get('node_url')
        if config_node not in host_list:
            host_list.append(config_node)
    except Exception:
        config_node = None

    # First check which nodes receive a ping
    hosts_found = []
    for host in host_list:
        try:
            host_ip = socket.gethostbyname(host)
            hosts_found.append((host, host_ip))
        except Exception:
            pass
    pickle_it('save', 'hosts_found.pkl', hosts_found)
    # Sample File format saved:
    # [('umbrel.local', '192.168.1.124'), ('mynode.local', '192.168.1.155'),
    #  ('raspberrypi.local', '192.168.1.102'),
    #  ('raspberrypi-2.local', '192.168.1.98')]

    # Now try to reach typical services
    port_list = [(80, 'Web Server'), (25441, 'Specter Server'),
                 (3002, 'Bitcoin RPC Explorer'),
                 (3006, 'Mempool.space Explorer'), (8082, 'Pi-Hole'),
                 (8091, 'VSCode Server'), (8085, 'Gitea'),
                 (3008, 'BlueWallet Lightning')]

    services_found = []
    for host in hosts_found:
        for port in port_list:
            try:
                url = 'http://' + host[0] + ':' + str(int(port[0])) + '/'
                result = tor_request(url)
                if not isinstance(result, requests.models.Response):
                    raise Exception(f'Did not get a return from {url}')
                if not result.ok:
                    raise Exception(
                        'Reached URL but did not get a code 200 [ok]')

                services_found.append((host, port))
            except Exception:
                pass

    pickle_it('save', 'services_found.pkl', services_found)
    pickle_it('save', 'services_refresh.pkl', datetime.now())
    # Sample File format saved to services_found
    # [(('umbrel.local', '192.168.1.124'), (80, 'Web Server')),
    #  (('umbrel.local', '192.168.1.124'), (25441, 'Specter Server')),
    #  (('umbrel.local', '192.168.1.124'), (3002, 'Bitcoin RPC Explorer')),
    #  (('umbrel.local', '192.168.1.124'), (3006, 'Mempool.space Explorer')),
    #  (('mynode.local', '192.168.1.155'), (80, 'Web Server'))]

    return (services_found)


def is_service_running(service):
    from node_warden import pickle_it
    services = pickle_it('load', 'services_found.pkl')
    found = False
    meta = []
    if services != 'file not found' and services is not None:
        for data in services:
            if service in data[1][1]:
                found = True
                meta.append(data)
    # Sample data return format
    # (True,
    #  [(('umbrel.local', '192.168.1.124'), (3002, 'Bitcoin RPC Explorer')),
    #   (('umbrel.local', '192.168.1.124'), (3006, 'Mempool.space Explorer'))])
    return (found, meta)
