#!/bin/bash
# Copyright (C) 2017-2022  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

echo
echo "========================================"
echo "Xilinx proprietary toolchain setup."
echo "----------------------------------------"

echo
echo "Fix up the Xilinx configuration directory"
echo "----------------------------------------"
mkdir -p ~/.Xilinx
ls -l ~/.Xilinx
mkdir ~/.ssh
echo
echo "Fixing loader to be able to run lmutils"
echo "----------------------------------------"
ln -s /lib64/ld-linux-x86-64.so.2 /lib64/ld-lsb-x86-64.so.3

export XILINX_LOCAL_USER_DATA=no
echo "----------------------------------------"

echo
echo "Select Xilinx Vivado version"
echo "----------------------------------------"
(
	set -e
	cd /opt
	if [ x"$XRAY_SETTINGS" = x"kintex7" ]; then
		echo "Using Xilinx Vivado Design Edition for $XRAY_SETTINGS build."
		echo
		ln -s /mnt/aux/Xilinx-design /opt/Xilinx
		ls -l Xilinx
		echo
	else
		ln -s /mnt/aux/Xilinx /opt/Xilinx
		echo "Using Xilinx Vivado WebPack Edition for $XRAY_SETTINGS build."
		ls -l Xilinx
	fi
)
echo "----------------------------------------"


echo
echo "List /opt directory"
echo "----------------------------------------"
ls -l /opt
echo "----------------------------------------"

echo $GHA_SSH_TUNNEL_CONFIG_SECRET_NAME
if [[ ! -z "$USE_LICENSE_SERVER" ]]; then

	echo
	echo "Xilinx license server ssh key found, checking the license"
	echo

	echo "127.0.0.1 xlic.int" | sudo tee -a /etc/hosts

	source /opt/Xilinx/Vivado/2017.2/settings64.sh
	export PATH=/opt/Xilinx/Vivado/2017.2/bin/unwrapped/lnx64.o:$PATH
	echo "-----"
	lmutil lmstat -a -c 2100@localhost -i || true
	echo "-----"

	export XILINXD_LICENSE_FILE=2100@localhost

else
	echo
	echo "**No** Xilinx license server ssh key found."
fi
echo "----------------------------------------"
