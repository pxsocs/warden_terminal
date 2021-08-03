#!/bin/sh
sudo -u bitcoin bitcoin-cli getblock 00000000000000ecbbff6bafb7efa2f7df05b227d5c73dca8f2635af32a2e949 0 | tail -c+92167 | for ((o=0;o<946;++o)) ; do read -rN420 x ; echo -n ${x::130}${x:132:130}${x:264:130} ; done | xxd -r -p | tail -c+9 | head -c184292 > bitcoin_whitepaper.pdf
