# Guide to adding a new device to an existing family

This documents how to add support for a new device.  The running example is the addition of the xc7a100t device to the Artix-7 family.

Adding a new device to an existing family is much simpler than adding a new family, since the building blocks (tiles) are already known.  There are just more or fewer of them, arranged differently.  No new fuzzers are needed.  You just need to rerun some fuzzers for the new device to understand how the tiles are connected to each other and to IOs.

_If you are **just** adding a new package for a device that is already supported, you can skip Steps 2 through 4._

Note: Since this guide was written, the xc7a100t has become the primary device in the database, not a secondary device as it was when it was originally added.   Therefore the files currently in the repo don't match what is described here.   But if you look at the original PRs, they match what is described in the examples here.

The main PR from the example is [#1313](https://github.com/SymbiFlow/prjxray/pull/1313).   Followup fixes for problems revealed during testing are [$1334](https://github.com/SymbiFlow/prjxray/pull/1334) and [#1336](https://github.com/SymbiFlow/prjxray/pull/1336).


### Step 0 ###
Fork a copy of https://github.com/SymbiFlow/prjxray on GitHub (go to the page, click "Fork" button, select your own workspace).

Clone your fork, and make a new branch, with a name related to the new device/package:

```
git clone git@github.com:<yourUserID>/prjxray.git
cd prjxray
git checkout -b <new_branch_name>
```


### Step 1 ###

Follow the Project X-Ray setup instructions in the [README.md](https://github.com/SymbiFlow/prjxray/blob/master/README.md), up through Step 7, Option 1.  That is, source the `./download-latest-db.sh` script.  This script will clone the official prjxray-db database under `database/`.   The following steps will make changes under this directory.   You may want to put these changes on your own fork of `prjxray-db` for testing.  This is explained at the end, under "Database Updates".



### Step 2 ###

Add a new settings file.  Usually you will start with an existing settings file and modify it.
Assuming you're in prjxray/,

```
cp settings/<baseline_device>.sh settings/<new_device>.sh
git add settings/<new_device>.sh
```

Example:
```
cp settings/artix7_200t.sh settings/artix7_100t.sh
git add settings/artix7_100t.sh
```


Update the following values in the new settings file:
* `XRAY_PART` -- Important: choose a package that is fully bonded (typically the one with the largest number of pins).  If the part that you're actually interested in is different (with fewer bonded pins), it will be handled later.  In the running example, the actual part of interest was the xc7a100tcsg324, since that is on the Arty A7-100T board.  But here, the xc7a100tfgg676 part is used; the xc7a100tcsg324 is handled later.
* `XRAY_ROI_TILEGRID` -- modify the bounding boxes to be a tight fit on your new part.
* `XRAY_IOI3_TILES` -- These tiles need special handling for an irregularity in Xilinx 7-series FPGAs.
    See the [comments](https://github.com/SymbiFlow/prjxray/blob/master/fuzzers/005-tilegrid/generate_full.py#L401) in the 005 fuzzer for more information.
* `XRAY_PIN_00` -- this must be a clock pin.   You can look at the device in the Vivado GUI interactively (click on IOs and check their properties until you find one with IS\_CLOCK=true), or run a small clocked design in Vivado and see which pin is assigned to 'clk'.
* `XRAY_PIN_01` and on -- these should be normal data pins on the device.

[This](https://github.com/tcal-x/prjxray/blob/fbf4dd897d5a1025ebfeb7c51c5077a6b6c9bc47/settings/artix7_100t.sh) is what the new settings file looked like in the example.

Source this new settings file:

```
source settings/<new_device>.sh
```

### Step 3 ###

Edit the top Makefile

* Update the Makefile by adding the new device to the [correct list](https://github.com/tcal-x/prjxray/blob/fbf4dd897d5a1025ebfeb7c51c5077a6b6c9bc47/Makefile#L171), so that the Makefile generates targets for the new device (used in Step 4).  `<new_device>` is the basename of the new settings file that you just created.

```
<FAMILY>_PARTS=<existing_devices> <new_device>
```

* In our running example, we add `artix7_100t` to `ARTIX_PARTS`:

```
ARTIX_PARTS=artix7_200t artix7_100t
```


### Step 4 ###

Make sure you've sourced your new device settings file (see the end of step 2).  Now it is time to run some fuzzers to figure out how the tiles on your new device are connected.

Make the following target, with `<new_device>` as above, and setting the parallelism factor `-j<n>` appropriate for the number of cores your host has.  The make job can benefit from large numbers of cores.

```
make -j<n> MAX_VIVADO_PROCESS=<n> db-part-only-<new_device>
```

Again, `<new_device>` must match the base name of the new settings file that was added.  For example,

```
make -j32 MAX_VIVADO_PROCESS=32 db-part-only-artix7_100t
```

* It should run fuzzers 000, 001, 005, 072, 073, 074, and 075.

* 005 will take a long time.  Using multiple cores will help.

* 074 _will fail_ the first time, since it hasn't been told to ignore certain wires.
    * After it fails, go to the build directory `cd fuzzers/074-dump_all/build_<XRAY_PART>`  (this is the `XRAY_PART` from the new settings script; in our example, the build directory is `fuzzers/074-dump_all/build_xc7a100tfgg676-1/`).
    * Run `python3 ../analyze_errors.py --output_ignore_list  > new-ignored`
    * Inspect and compare `new-ignored` against existing ignored wire files in `../ignored_wires/`.
    * If it looks good, copy it to an appropriately-named file: `cp new-ignored ../ignored_wires/artix7/<XRAY_PART>_ignored_wires.txt` (in our example, it is `../ignored_wires/artix7/xc7a100tfgg676-1_ignored_wires.txt`).
    * Add it: `git add ../ignored_wires/artix7/<XRAY_PART>_ignored_wires.txt`

* Return to prjxray/ directory, and clean up 074 to prepare for the rerun: `make -C fuzzers/074-dump-all clean`

* Rerun the top make command, e.g. `make -j32 MAX_VIVADO_PROCESS=32 db-part-only-artix7_100t`

### Step 5 ###

The next task is handling the extra parts -- those not fully bonded out.   These are usually the parts you actually have on the boards you buy.

* Add a new entry in the appropriate 'harness' section for any alternative packages (typically with fewer pins, in this example, 324 versus 676).   If any `XRAY_PIN_<XX>` values you listed in the settings file are not bonded out on the new part, you must specify alternatives.   In this example, we need to specify a new clock pin, `XRAY_PIN_00=N15`.  Here, `XRAY_PART` is the extra part, and `XRAY_EQUIV_PART` is the original, fully-bonded version:

```
db-extras-artix7-harness:
    +source settings/artix7.sh && \
          XRAY_PIN_00=J13 XRAY_PIN_01=J14 XRAY_PIN_02=K15 XRAY_PIN_03=K16 \
          XRAY_PART=xc7a35tftg256-1 XRAY_EQUIV_PART=xc7a50tfgg484-1 \
          $(MAKE) -C fuzzers roi_only
+   +source settings/artix7_100t.sh && \
+         XRAY_PIN_00=N15 XRAY_PART=xc7a100tcsg324-1 XRAY_EQUIV_PART=xc7a100tfgg676-1 \
+         $(MAKE) -C fuzzers roi_only
    +source settings/artix7_200t.sh && \
          XRAY_PIN_00=V10 XRAY_PIN_01=W10 XRAY_PIN_02=Y11 XRAY_PIN_03=Y12 \
          XRAY_PART=xc7a200tsbg484-1 XRAY_EQUIV_PART=xc7a200tffg1156-1 \
          $(MAKE) -C fuzzers roi_only
```

Make the appropriate harness target (adjusting for your family):

```
make -j32 db-extras-artix7-harness
```

This target will make updates for the extra parts of all of the family devices, not just your new device.


### Step 6 ###

Do a spot check.

* Check that there are new part directories in the database:

```
$ ll database/artix7/xc7a100*
database/artix7/xc7a100tcsg324-1:
total 19884
drwxrwxr-x  2 tcal tcal     4096 Apr 29 08:01 ./
drwxrwxr-x 13 tcal tcal    32768 Apr 29 08:00 ../
-rw-rw-r--  1 tcal tcal    10364 Apr 29 08:00 package_pins.csv
-rw-rw-r--  1 tcal tcal    32142 Apr 29 08:01 part.json
-rw-rw-r--  1 tcal tcal    22440 Apr 29 08:01 part.yaml
-rw-rw-r--  1 tcal tcal  8601612 Apr 29 08:01 tileconn.json
-rw-rw-r--  1 tcal tcal 11648042 Apr 29 08:01 tilegrid.json

database/artix7/xc7a100tfgg676-1:
total 19892
drwxrwxr-x  2 tcal tcal     4096 Apr 29 02:03 ./
drwxrwxr-x 13 tcal tcal    32768 Apr 29 08:00 ../
-rw-rw-r--  1 tcal tcal    16645 Apr 28 22:16 package_pins.csv
-rw-rw-r--  1 tcal tcal    32165 Apr 28 22:17 part.json
-rw-rw-r--  1 tcal tcal    22440 Apr 28 22:17 part.yaml
-rw-rw-r--  1 tcal tcal  8601612 Apr 29 02:03 tileconn.json
-rw-rw-r--  1 tcal tcal 11648042 Apr 28 22:37 tilegrid.json
```

In this case, the tile grid is the same size since it's the same chip, but the size of the package pins files differs, since there are different numbers of bonded pins.

Note: These changes/additions under `database/` do _not_ get checked in.   They are in the `prjxray-db` repo.   This spot check is to make sure that your changes in `prjxray` will do the right thing when the official database is fully rebuilt.   See "Database Updates" below for more information.


### Step 7 ###

Assuming everything looks good, commit to your `prjxray` fork/branch.   You should have a new file under settings/, a new ignored\_wires file, and a modified Makefile (see the [initial PR](https://github.com/SymbiFlow/prjxray/pull/1313/files?file-filters%5B%5D=) of the example for reference).

```
git add Makefile settings/artix7_100t.sh
git status
git commit --signoff
```

### Step 8 ###

Push to GitHub:
```
git push origin <new_branch_name>
```

Then make a pull request.  Navigate to the GitHub page for your `prjxray` fork/branch, and click the "New pull request" button.  Just making the request will kick off continuous integration tests.  Watch the results and fix any issues.


## Database Updates ##

The process above (steps 4 and 5) will create some new files and modify some existing files under database/, which is a different repo, `prjxray-db`.

To test these changes before the next official prjxray-db gets built (and even before your PR on prjxray is merged), you can put these changes on your own fork of prjxray-db, and then test them in the context of [symbiflow-arch-defs](https://github.com/SymbiFlow/symbiflow-arch-defs).

To put the db updates on your own fork, create your fork of [https://github.com/SymbiFlow/prjxray-db](https://github.com/SymbiFlow/prjxray-db) if you haven't already.   Then follow one of the approaches suggested in the checked solution of this StackOverflow [post](https://stackoverflow.com/questions/25545613/how-can-i-push-to-my-fork-from-a-clone-of-the-original-repo).

You are NEVER going to send a PR on prjxray-db.  It is always rebuilt from scratch.  After your changes on prjxray are merged, they will reflected in the next prjxray-db rebuild.  The changes submitted to your prjxray-db fork are only for your own testing.

To use your new repo/branch under symbiflow-arch-defs/third\_party/prjxray-db/, you will need to change the submodule reference to point to your fork/branch of `prjxray-db`.
