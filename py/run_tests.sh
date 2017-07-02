#!/bin/bash
LogFile='application.log'
LogDir='.'
LogPath="$LogDir/$LogFile"
/usr/bin/savelog -l -p -d -C -c 5 "$LogPath"
time /usr/bin/python2 -m fer.compiler tests/basic/test.fer 1>>"$LogPath" 2>&1
