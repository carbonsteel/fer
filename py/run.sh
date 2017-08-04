#!/bin/bash
LogFile='application.log'
LogDir='.'
LogPath="$LogDir/$LogFile"
./tools/savelog -l -p -d -C -c 5 "$LogPath"
export INCPATH='lang/tests/basic;lang/include'
time /usr/bin/python3.6 -OO -m fer.compiler basic 1>>"$LogPath" 2>&1
