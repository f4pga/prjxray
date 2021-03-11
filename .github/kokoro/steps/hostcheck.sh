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

	exit $MOUNT_RET
fi
