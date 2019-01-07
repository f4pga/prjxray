# header for fuzzer generate.sh scripts

if [ -z "$XRAY_DATABASE" ]; then
	echo "No XRAY environment found. Make sure to source the settings file first!"
	exit 1
fi

set -ex

export FUZDIR=$PWD

# for some reason on sourced script set -e doesn't work
# Scripts may have additional arguments, but first is reserved for build directory
test $# -ge 1 || exit 1
test ! -e "$SPECDIR"
export SPECDIR=$1

mkdir -p "$SPECDIR"
cd "$SPECDIR"

export SEED="$(echo $SPECDIR | md5sum | cut -c1-8)"
export SEEDN="$(basename $(pwd) |sed s/specimen_0*//)"

function seed_vh () {
    echo '`define SEED 32'"'h${SEED}" > setseed.vh
}

