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
echo "Waiting for storage"
echo "----------------------------------------"
STORAGE_CHECK_ATTEMPTS=1
while true; do
       # Check that tmpfs has been mounted correctly.
       set -x +e
       mount | grep /tmpfs
       MOUNT_RET=$?
       set +x -e
       if [[ $MOUNT_RET == 0 ]] ; then
               break;
       else
               echo "----------------------------------------"
               echo "Error: No storage is mounted on /tmpfs."
               echo "----------------------------------------"
               echo ""
       fi

       # Dump debugging information.
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

       # Fail if we have waited to long.
       if [[ $STORAGE_CHECK_ATTEMPTS -gt 5 ]]; then
               exit $MOUNT_RET
       else
               STORAGE_CHECK_ATTEMPTS=$(( $STORAGE_CHECK_ATTEMPTS + 1 ))
       fi

       # Wait for a bit before rechecking.
       SLEEP_FOR=$(( STORAGE_CHECK_ATTEMPTS * 10 ))
       echo ""
       echo "Sleeping for $SLEEP_FOR seconds before trying again..."
       sleep $SLEEP_FOR
done
