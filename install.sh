#!/bin/bash

if [[ $EUID -ne 0 ]]; then
	echo "Error: MUST run script with root"
	exit -1
fi




install -p -D -o root -g root -m 0755 ./sc_ddns.py /usr/local/bin/
install -p -D -o root -g root -m 0755 ./sc_ddns_env /etc/sc_ddns/environment
install -p -D -o root -g root -m 0644 ./sc_ddns.service /etc/systemd/system/
install -p -D -o root -g root -m 0644 ./sc_ddns.timer /etc/systemd/system/

