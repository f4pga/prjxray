#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -e

echo
echo "========================================"
echo "Removing older packages"
echo "----------------------------------------"
sudo apt-get remove -y cmake
echo "----------------------------------------"

echo
echo "========================================"
echo "Update the CA certificates"
echo "----------------------------------------"
sudo apt-get install -y ca-certificates
echo "----------------------------------------"
sudo update-ca-certificates
echo "----------------------------------------"

echo
echo "========================================"
echo "Remove the expire letsencrypt.org cert "
echo "----------------------------------------"
wget https://helloworld.letsencrypt.org/ || true
echo "----------------------------------------"
sudo rm /usr/share/ca-certificates/mozilla/DST_Root_CA_X3.crt
echo "----------------------------------------"
sudo update-ca-certificates
echo "----------------------------------------"
wget https://helloworld.letsencrypt.org/ || true
echo "----------------------------------------"


echo
echo "========================================"
echo "Host adding PPAs"
echo "----------------------------------------"
wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | sudo apt-key add -
sudo apt-add-repository 'deb https://apt.kitware.com/ubuntu/ xenial main'
sudo add-apt-repository ppa:deadsnakes/ppa
echo "----------------------------------------"

echo
echo "========================================"
echo "Host updating packages"
echo "----------------------------------------"
sudo apt-get update
echo "----------------------------------------"

echo
echo "========================================"
echo "Host remove packages"
echo "----------------------------------------"
sudo apt-get remove -y \
	python-pytest \


sudo apt-get autoremove -y

echo "----------------------------------------"
echo
echo "========================================"
echo "Host install packages"
echo "----------------------------------------"
sudo apt-get install -y \
        bash \
        bison \
        build-essential \
        ca-certificates \
        clang-format \
        cmake \
        colordiff \
        coreutils \
        curl \
        flex \
        fontconfig \
        git \
        jq \
        lsb \
        nodejs \
        psmisc \
        python3 \
        python3-dev \
        python3-venv

echo "========================================"
echo "Enter virtual env for python 3.8"
echo "----------------------------------------"
python3 -mvenv startup_python
source startup_python/bin/activate
which python
python --version
which python3
python3 --version

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

echo
echo "========================================"
echo "Getting diff2html to produce pretty database diffs"
echo "----------------------------------------"
(
	sudo npm install -g diff2html-cli
)
