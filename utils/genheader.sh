# header for fuzzer generate.sh scripts

if [ -z "$XRAY_DATABASE" ]; then
	echo "No XRAY environment found. Make sure to source the settings file first!"
	exit 1
fi

set -ex

test $# = 1
test ! -e $1
mkdir $1
cd $1

