#!/bin/bash

# Fix up things related to Xilinx tool chain.

ls -l ~/.Xilinx
sudo chown -R $USER ~/.Xilinx

export XILINX_LOCAL_USER_DATA=no
