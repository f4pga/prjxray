Vagrant config for constructing a prjxray development environment.

* Install vagrant and virtualbox
* Download Vivado full installer (should be ~16GB)
* Extract the Vivado tar.gz
* Move the extracted installer (Xilinx\_Vivado\_SDK\_<version>) to this directory
* Rename the Vivado installer folder to 'Vivado'
* Run 'vagrant up'

Be patient.  While the VM will start with an Ubuntu image quickly, all of the
desktop packages need to be installed followed by Vivado.  File-sharing with
the VM uses NFS by default for speed.  You may need to install nfsd if you are
using Linux.  macOS includes ones.

After 'vagrant up' has finished, the VM will be booted and ready.  This
directory is mounted at /vagrant and the parent directory is mounted at
/prjxray.  In most cases, you'll want to change to /prjxray and follow the
instructions in README.md.

Vivado WEBPACK edition is installed.  No license is required for the artix7 part of
interest (xc7a50tfgg484).
