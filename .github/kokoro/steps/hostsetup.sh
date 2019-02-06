#!/bin/bash

set -e

echo
echo "========================================"
echo "Host updating packages"
echo "----------------------------------------"
sudo apt-get update
echo "----------------------------------------"

echo
echo "========================================"
echo "Host install packages"
echo "----------------------------------------"
sudo apt-get install -y \
        bison \
        build-essential \
        ca-certificates \
        clang-format \
        cmake \
        curl \
        flex \
        fontconfig \
        git \
        jq \
        psmisc \
        python \
        python3 \
        python3-dev \
        python3-virtualenv \
        python3-yaml \
        virtualenv \

echo "----------------------------------------"

(
	cd /tmp
	# Upgrade pstree to support the -T flag.
	wget https://storage.googleapis.com/prjxray-deps-debs/psmisc_23.2-1_amd64.deb
	sudo dpkg --install psmisc_23.2-1_amd64.deb
	which pstree
	pstree --help || true
)

echo "----------------------------------------"
