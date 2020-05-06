#!/usr/bin/env tclsh
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# From: https://gist.github.com/yyamasak/af250f7ca74e18526734#file-reformat-tcl-L10
# Which is based on https://wiki.tcl-lang.org/page/Reformatting+Tcl+code+indentation
# See for licensing

proc reformat {tclcode {pad 4}} {
    set lines [split $tclcode \n]
    set out ""
    set continued no
    set oddquotes 0
    set line [lindex $lines 0]
    set indent [expr {([string length $line]-[string length [string trimleft $line \ \t]])/$pad}]
    set pad [string repeat " " $pad]

    foreach orig $lines {
        set newline [string trim $orig \ \t]
        set line [string repeat $pad $indent]$newline
        if {[string index $line end] eq "\\"} {
            if {!$continued} {
                incr indent 2
                set continued yes
            }
        } elseif {$continued} {
            incr indent -2
            set continued no
        }

        if { ! [regexp {^[ \t]*\#} $line] } {

            # oddquotes contains : 0 when quotes are balanced
            # and 1 when they are not
            set oddquotes [expr {([count $line \"] + $oddquotes) % 2}]
            if {! $oddquotes} {
                set  nbbraces  [count $line \{]
                incr nbbraces -[count $line \}]
                set brace   [string equal [string index $newline end] \{]
                set unbrace [string equal [string index $newline 0] \}]
                if {$nbbraces!=0 || $brace || $unbrace} {
                    incr indent $nbbraces ;# [GWM] 010409 multiple close braces
                    if {$indent<0} {
                        error "unbalanced braces"
                    }
                    puts $unbrace
                    puts $pad
                    puts $nbbraces
                    set np [expr {$unbrace? [string length $pad]:-$nbbraces*[string length $pad]}]
                    set line [string range $line $np end]
                }
            } else {
                # unbalanced quotes, preserve original indentation
                set line $orig
            }
        }
        append out $line\n
    }
    return $out
}

proc eol {} {
    switch -- $::tcl_platform(platform) {
        windows {return \r\n}
        unix {return \n}
        macintosh {return \r}
        default {error "no such platform: $::tc_platform(platform)"}
    }
}

proc count {string char} {
    set count 0
    while {[set idx [string first $char $string]]>=0} {
        set backslashes 0
        set nidx $idx
        while {[string equal [string index $string [incr nidx -1]] \\]} {
            incr backslashes
        }
        if {$backslashes % 2 == 0} {
            incr count
        }
        set string [string range $string [incr idx] end]
    }
    return $count
}

set usage "reformat.tcl ?-indent number? filename"

if {[llength $argv]!=0} {
    if {[lindex $argv 0] eq "-indent"} {
        set indent [lindex $argv 1]
        set argv [lrange $argv 2 end]
    } else  {
        set indent 4
    }
    if {[llength $argv]>1} {
        error $usage
    }
    set f [open $argv r]
    set data [read $f]
    close $f

    set filename "$argv.tmp"
    set f [open $filename  w]

    puts -nonewline $f [reformat [string map [list [eol] \n] $data] $indent]
    close $f
    file copy -force $filename  $argv
    file delete -force $filename

}
