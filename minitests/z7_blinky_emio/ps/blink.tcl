connect
targets -set -nocase -filter {name =~ "ARM* #0"}
rst -system
dow blink.elf
con
