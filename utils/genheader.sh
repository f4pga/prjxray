# header for fuzzer generate.sh scripts

if [ -z "$XRAY_DATABASE" ]; then
	echo "No XRAY environment found. Make sure to source the settings file first!"
	exit 1
fi

set -ex

# for some reason on sourced script set -e doesn't work
test $# = 1 || exit 1
test ! -e "$SPECN"
SPECN=$1

mkdir "$SPECN"
cd "$SPECN"

export SEED="$(echo $SPECN | md5sum | cut -c1-8)"
export SEEDN="$(basename $(pwd) |sed s/specimen_0*//)"

function seed_vh () {
    echo '`define SEED 32'"'h${SEED}" > setseed.vh
}

