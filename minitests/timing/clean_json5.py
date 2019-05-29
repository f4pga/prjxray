import pyjson5
import simplejson
import sys


def main():
    simplejson.dump(pyjson5.load(sys.stdin), sys.stdout, indent=2)


if __name__ == "__main__":
    main()
