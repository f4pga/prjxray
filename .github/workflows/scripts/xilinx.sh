#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
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
#sudo chown -R $USER ~/.Xilinx
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

# Create a tunnel to the server which has the Xilinx licenses and port forward
# them.
echo
echo "Setting up license server tunnel"
echo "----------------------------------------"
if [ ! -z "$LICENSE_TUNNEL_KEY_DATA" ]; then
	LICENSE_TUNNEL_KEY=~/.Xilinx/xilinx-tunnel-key
	LICENSE_TUNNEL_HOST=10.138.0.3
	echo $LICENSE_TUNNEL_KEY_DATA | base64 --decode > $LICENSE_TUNNEL_KEY

	echo "SSH Key for license server tunnel should be found @ $LICENSE_TUNNEL_KEY"
	ls -l $LICENSE_TUNNEL_KEY || true

	echo
	echo "Xilinx license server ssh key found, setting up tunnel"
	echo

	echo
	echo "Checking $LICENSE_TUNNEL_HOST is up"
	ip addr show
	echo "ping: ---------"
	ping -c 5 $LICENSE_TUNNEL_HOST
	echo "port: ---------"
	nc -zv $LICENSE_TUNNEL_HOST 22
	echo "---------"
	echo

	chmod 600 $LICENSE_TUNNEL_KEY
	cat <<EOF > ssh_config
Host xilinx-license
  HostName $LICENSE_TUNNEL_HOST
  User kokoro
  IdentityFile $LICENSE_TUNNEL_KEY
  StrictHostKeyChecking no
  ExitOnForwardFailure yes
  # SessionType none
  LocalForward localhost:2100 172.18.0.3:2100
  LocalForward localhost:2101 172.18.0.3:2101
EOF
	echo "127.0.0.1 xlic.int" | sudo tee -a /etc/hosts

	export GIT_SSH_COMMAND="ssh -F $(pwd)/ssh_config -f -N"
	${GIT_SSH_COMMAND} xilinx-license

	(
		source /opt/Xilinx/Vivado/2017.2/settings64.sh
		export PATH=/opt/Xilinx/Vivado/2017.2/bin/unwrapped/lnx64.o:$PATH
		echo "-----"
		lmutil lmstat -a -c 2100@localhost -i || true
		echo "-----"
	)

	export XILINXD_LICENSE_FILE=2100@localhost

else
	echo
	echo "**No** Xilinx license server ssh key found."
fi
echo "----------------------------------------"
