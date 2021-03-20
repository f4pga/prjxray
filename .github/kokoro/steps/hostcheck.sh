#!/bin/bash
# Copyright (C) 2017-2021  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -e

echo
echo "========================================"
echo "Check storage"
echo "----------------------------------------"
# Wait 30 seconds to not check the storage too early.
sleep 30
set -x +e
mount | grep /tmpfs
MOUNT_RET=$?
set +x -e
if [[ $MOUNT_RET != 0 ]] ; then
	echo "----------------------------------------"
	echo "Error: No storage is mounted on /tmpfs."
	echo "----------------------------------------"

	echo "========================================"
	echo "Dmesg dump"
	echo "----------------------------------------"
	dmesg

	echo "========================================"
	echo "Partition information"
	echo "----------------------------------------"
	echo ""
	echo "partprobe"
	echo "----------------------------------------"
	partprobe -s
	echo ""
	echo "cat /proc/partitions"
	echo "----------------------------------------"
	cat /proc/partitions
	echo ""
	echo "cat /etc/fstab"
	echo "----------------------------------------"
	cat /etc/fstab
	echo ""
	echo "cat /etc/mtab"
	echo "----------------------------------------"
	cat /etc/mtab
	echo ""
	echo "lsblk"
	echo "----------------------------------------"
	lsblk --list --output 'NAME,KNAME,FSTYPE,MOUNTPOINT,LABEL,UUID,PARTTYPE,PARTLABEL,PARTUUID'
	echo ""
	echo "sfdisk"
	echo "----------------------------------------"
	sudo sfdisk --list
	echo ""
	echo "systemctl | grep mount"
	echo "----------------------------------------"
	systemctl | grep mount
	echo ""
	echo "systemctl | grep dev"
	echo "----------------------------------------"
	systemctl | grep dev

	exit $MOUNT_RET
fi
