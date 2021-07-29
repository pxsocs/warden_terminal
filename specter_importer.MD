# Specter Importer Class

## Getting Started

Create an empty class instance:

```python
from specter_importer import Specter
specter = Specter()
```

## Methods

### Wallet Alias List

Returns a list of wallet aliases

Input:

```python
specter.wallet_alias_list()
```

Output:

```bash
{'trezor', 'coldcard', 'etc', 'etc'}
```

### Transaction List

Returns Transaction List
`load=True` loads local file (not from server)
Payload can be modified as below

Input:

```python
# Optional: Modify Payload
specter.tx_payload = {
            'idx': 0,
            'limit': 1,
            'search': None,
            'sortby': 'time',
            'sortdir': 'desc'
}
specter.refresh_txs(load=True)
```

Output:

```json
{
  "pageCount": 10,
  "txlist": [
    {
      "txid": "<hidden>",
      "blockhash": "2bcf3",
      "blockheight": 667593,
      "time": 1611578028,
      "conflicts": [],
      "bip125-replaceable": "no",
      "hex": "<deleted>",
      "vsize": 1868,
      "category": "receive",
      "address": "<hidden>",
      "amount": 0.00001,
      "ismine": True,
      "confirmations": 18,
      "label": "Addess 1",
      "validated_blockhash": "",
      "wallet_alias": "trezor"
    }
  ],
  "last_update": "01/01/2021, 00:00:01"
}
```

### Wallet Info Scraper

Returns more wallet info from settings

Input

```python
specter.wallet_info(<wallet_alias>, load=False)
```

Output

```json
{
    'url': 'http://127.0.0.1:25441/wallets/wallet/<alias>/settings/',
    'title': 'Devices',
    'subtitle': '1 out of 2 multisig',
    'devices':
        {'coldcard':
            {'url': '/devices/device/coldcard/',
            'image': 'http://127.0.0.1:25441/static/img/devices/coldcard_icon.svg',
            'name': 'ColdCard'
            },
        'trezor':
            {'url': '/devices/device/trezor/', '
            image': 'http://127.0.0.1:25441/static/img/devices/trezor_icon.svg',
            'name': 'Trezor'}}}
```

### Home Page Scraper

Returns a metadata dictionary sourced from Specter's front page

Input

```python
meta = specter.home_parser()
```

Output

```json
{
    'version': '1.1.0',
    'bitcoin_core_html': '<table></table>,
    'bitcoin_core_data':
        {'Network': ' main ',
        'Bitcoin Core Version': ' v0.20.1 (200100) ',
        'Connections count': ' 10 ',
        'Difficulty': ' 21434395961348 ',
        'Size on disk': ' 345 GB ',
        'Blocks count': ' 669397 ',
        'Last block hash': ' <hidden>',
        'Mempool Size': ' 41440 transactions ',
        'Node uptime': ' ~ 457 Hours '},
    'alias_list': ['1', '2'],
    'wallet_dict': {
        '1': {
            'url': 'http://127.0.0.1:25441/wallets/wallet/1/',
            'name': '1',
            'keys': 'Single Key'
            },
        '2': {
            'url': 'http://127.0.0.1:25441/wallets/wallet/2/',
            'name': '2',
            'keys': 'Single Key'},
        },
    'device_list': ['1', '2'],
    'device_dict':
        {'1': {
            'url': 'http://127.0.0.1:25441/devices/device/1/',
            'image': 'http://127.0.0.1:25441/static/img/devices/coldcard_icon.svg',
            'name': '1',
            'keys': '1 keys'}
                }
}

```
