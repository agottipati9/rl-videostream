#!/bin/bash

sudo apt install protobuf-compiler libprotobuf-dev autotools-dev dh-autoreconf iptables pkg-config dnsmasq-base apache2-bin debhelper libssl-dev ssl-cert libxcb-present-dev libcairo2-dev libpango1.0-dev apache2-dev  
git clone https://github.com/ravinet/mahimahi
cd mahimahi
./autogen.sh
./configure
make
sudo make install
sudo sysctl -w net.ipv4.ip_forward=1