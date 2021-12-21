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
ls -l ~/.Xilinx
sudo chown -R $USER ~/.Xilinx

export XILINX_LOCAL_USER_DATA=no
echo "----------------------------------------"

echo
echo "Select Xilinx Vivado version"
echo "----------------------------------------"
(
	set -e
	cd /opt
	if [ x"$XRAY_SETTINGS" = x"kintex7" ]; then
		echo "---"
		mount
		sudo mount -o remount,rw /opt
		mount
		echo "---"
		echo
		echo "Using Xilinx Vivado Design Edition for $XRAY_SETTINGS build."
		sudo rm -f Xilinx
		sudo ln -s Xilinx-design Xilinx
		ls -l Xilinx
		echo
		echo "---"
		sudo mount -o remount,ro /opt
		mount
		echo "---"
	else
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

LICENSE_TUNNEL_KEY=$KOKORO_KEYSTORE_DIR/74045_foss-fpga-tools_xilinx-license
echo "SSH Key for license server tunnel should be found @ $LICENSE_TUNNEL_KEY"
ls -l $LICENSE_TUNNEL_KEY || true

if [ -f $LICENSE_TUNNEL_KEY ]; then
	echo
	echo "Xilinx license server ssh key found, setting up tunnel"

	chmod 600 $LICENSE_TUNNEL_KEY
	cat <<EOF > ssh_config
Host xilinx-license
  HostName 10.128.15.194
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
