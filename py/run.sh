#!/bin/bash
LogFile='application.log'
LogDir='.'
LogPath="$LogDir/$LogFile"
/usr/bin/savelog -l -p -d -C -c 5 "$LogPath"
export INCPATH='tests/basic;src/include'
time /usr/bin/python3.6 -m fer.compiler basic 1>>"$LogPath" 2>&1
