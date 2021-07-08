#!/bin/sh
cd /build
service tor start
python3 node_warden.py
